# services/logo_generator.py
"""
Logo generation service using Pillow.
Handles all image composition and format conversion.
"""

import os
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from algorithms.text_splitter import split_unit_name
from config.constants import (
    LOGO_ASSETS_PATH, ARMOIRIES_FILE, LIGNE_ETAT_FILE, FONT_FILE,
    ARMOIRIES_HEIGHT, SPACING, TEXT_SPACING, FONT_SIZE,
    LINE_SPACING, TEXT_COLOR
)

class LogoGeneratorService:
    """Service for generating RDC logos with Pillow"""

    def __init__(self, logo_assets_base_path: str = None):
        """
        Initialize service with asset paths.

        Args:
            logo_assets_base_path: Base path to logo assets directory (defaults to LOGO_ASSETS_PATH)
        """
        if logo_assets_base_path is None:
            logo_assets_base_path = LOGO_ASSETS_PATH

        self.logo_assets_base = logo_assets_base_path
        self.armoiries_path = os.path.join(logo_assets_base_path, ARMOIRIES_FILE)
        self.ligne_etat_path = os.path.join(logo_assets_base_path, LIGNE_ETAT_FILE)
        self.font_path = FONT_FILE

    def generate_logo(
        self,
        unit_nom: str,
        language: str = 'fr',
        armoiries_height: int = None,
        spacing: int = None,
        text_spacing: int = None,
        font_size: int = None,
        line_spacing: int = None,
        text_color: tuple = None
    ) -> BytesIO:
        """
        Generate logo as PNG BytesIO.

        Args:
            unit_nom: Institution/unit name
            language: Language code (unused for now, but for future i18n)
            armoiries_height: Height of armoiries in pixels
            spacing: Gap between armoiries and ligne_etat
            text_spacing: Gap between ligne_etat and text
            font_size: Font size for text
            line_spacing: Vertical spacing between lines
            text_color: RGBA color tuple for text

        Returns:
            BytesIO containing PNG image (RGBA)
        """
        # Use defaults if not provided
        armoiries_height = armoiries_height or ARMOIRIES_HEIGHT
        spacing = spacing or SPACING
        text_spacing = text_spacing or TEXT_SPACING
        font_size = font_size or FONT_SIZE
        line_spacing = line_spacing or LINE_SPACING
        text_color = text_color or TEXT_COLOR

        # Validate and load assets
        self._validate_assets()

        # Load images
        armoiries = Image.open(self.armoiries_path).convert('RGBA')
        ligne_etat = Image.open(self.ligne_etat_path).convert('RGBA')

        # Resize armoiries to specified height (maintain aspect ratio)
        armoiries = self._resize_image_by_height(armoiries, armoiries_height)

        # Resize ligne_etat to match armoiries height
        ligne_etat = self._resize_image_by_height(ligne_etat, armoiries_height)

        # Split institution name into lines
        text_lines = split_unit_name(unit_nom)

        if not text_lines:
            raise ValueError("Institution name cannot be empty")

        # Load font
        font = ImageFont.truetype(self.font_path, font_size)

        # Calculate text dimensions
        text_width, text_height = self._calculate_text_dimensions(
            text_lines, font, line_spacing
        )

        # Create canvas
        canvas_width = armoiries.width + spacing + ligne_etat.width + text_spacing + text_width
        canvas_height = armoiries.height
        canvas = Image.new('RGBA', (canvas_width, canvas_height), (255, 255, 255, 0))

        # Paste armoiries (left-aligned)
        armoiries_x = 0
        armoiries_y = (canvas_height - armoiries.height) // 2
        canvas.paste(armoiries, (armoiries_x, armoiries_y), armoiries)

        # Paste ligne_etat
        ligne_x = armoiries_x + armoiries.width + spacing
        ligne_y = (canvas_height - ligne_etat.height) // 2
        canvas.paste(ligne_etat, (ligne_x, ligne_y), ligne_etat)

        # Draw text
        text_x = ligne_x + ligne_etat.width + text_spacing
        text_y = (canvas_height - text_height) // 2

        draw = ImageDraw.Draw(canvas)
        current_y = text_y

        for line in text_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_height = bbox[3] - bbox[1]

            draw.text(
                (text_x, current_y),
                line,
                fill=text_color,
                font=font
            )
            current_y += line_spacing

        # Save to BytesIO
        buf = BytesIO()
        canvas.save(buf, format='PNG')
        buf.seek(0)

        return buf

    def convert_png_to_jpg(self, png_buf: BytesIO, quality: int = 95) -> BytesIO:
        """
        Convert PNG (RGBA) to JPG (RGB) with white background.

        Args:
            png_buf: BytesIO containing PNG image
            quality: JPEG quality (1-100)

        Returns:
            BytesIO containing JPEG image
        """
        png_buf.seek(0)
        png_img = Image.open(png_buf).convert('RGBA')

        # Create white background
        background = Image.new('RGB', png_img.size, (255, 255, 255))

        # Composite PNG on background
        background.paste(png_img, mask=png_img.split()[3])

        # Save to BytesIO
        buf = BytesIO()
        background.save(buf, format='JPEG', quality=quality)
        buf.seek(0)

        return buf

    def _validate_assets(self):
        """Validate that all required asset files exist"""
        for path, name in [
            (self.armoiries_path, 'Armoiries'),
            (self.ligne_etat_path, 'Ligne d\'État'),
            (self.font_path, 'Font')
        ]:
            if not os.path.exists(path):
                raise FileNotFoundError(f"{name} file not found: {path}")

    def _resize_image_by_height(self, img: Image.Image, target_height: int) -> Image.Image:
        """Resize image to target height, maintaining aspect ratio"""
        ratio = target_height / img.height
        new_width = int(img.width * ratio)
        return img.resize((new_width, target_height), Image.Resampling.LANCZOS)

    def _calculate_text_dimensions(
        self,
        lines: list,
        font: ImageFont.FreeTypeFont,
        line_spacing: int
    ) -> tuple:
        """
        Calculate total width and height of text block.

        Returns:
            (max_width, total_height)
        """
        draw = ImageDraw.Draw(Image.new('RGBA', (1, 1)))

        max_width = 0
        total_height = 0

        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]

            max_width = max(max_width, line_width)

            if i == 0:
                total_height = line_height
            else:
                total_height += line_spacing

        return (max_width, total_height)
