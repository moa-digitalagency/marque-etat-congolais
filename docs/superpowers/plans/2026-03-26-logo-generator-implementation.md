# Logo Generator WebApp Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use [superpowers:subagent-driven-development](superpowers:subagent-driven-development) (recommended) or [superpowers:executing-plans](superpowers:executing-plans) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete Flask webapp for generating DRC government logos with user authentication, template management, history tracking, and public sharing.

**Architecture:**
- Monolithic Flask app with SQLAlchemy ORM and PostgreSQL
- Modular structure (algorithms, services, routes, models)
- Pillow-based image generation (PNG/JPG)
- Jinja2 templates + Tailwind CSS + vanilla JS frontend
- Multi-language support (FR, Lingala, Swahili)

**Tech Stack:** Flask 3.0+, SQLAlchemy 2.0+, PostgreSQL 14+, Pillow 10.0+, Tailwind CSS, bcrypt, Flask-Login

---

## Phase 1: Project Setup & Configuration

### Task 1: Create Directory Structure & init Python packages

**Files:**
- Create: `algorithms/__init__.py`
- Create: `config/__init__.py`
- Create: `models/__init__.py`
- Create: `routes/__init__.py`
- Create: `services/__init__.py`
- Create: `security/__init__.py`
- Create: `utils/__init__.py`
- Create: `scripts/__init__.py`
- Create: `tests/__init__.py`
- Create: `statics/css/`, `statics/js/`, `statics/uploads/logos/`
- Create: `templates/auth/`, `templates/public/`, `templates/dashboard/`, `templates/admin/`
- Create: `lang/`, `docs/`

- [ ] **Step 1: Create directory structure**

```bash
cd /Users/moadigitalagency/marque-etat-congolais

# Create all directories
mkdir -p algorithms config models routes services security utils scripts tests
mkdir -p statics/{css,js,uploads/logos,img,font}
mkdir -p templates/{auth,public,dashboard,admin}
mkdir -p lang docs/superpowers/{specs,plans}

# Create __init__.py files
touch algorithms/__init__.py config/__init__.py models/__init__.py routes/__init__.py
touch services/__init__.py security/__init__.py utils/__init__.py scripts/__init__.py tests/__init__.py
```

- [ ] **Step 2: Verify structure created**

```bash
ls -la algorithms config models routes services | head -5
```

Expected: All directories and __init__.py files exist.

---

### Task 2: Create requirements.txt with all dependencies

**Files:**
- Create: `requirements.txt`

- [ ] **Step 1: Write requirements.txt**

```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
SQLAlchemy==2.0.23
psycopg2-binary==2.9.9
Pillow==10.1.0
bcrypt==4.1.1
python-dotenv==1.0.0
WTForms==3.1.1
email-validator==2.1.0
gunicorn==21.2.0
pytest==7.4.3
pytest-flask==1.3.0
```

- [ ] **Step 2: Verify file created**

```bash
cat requirements.txt | head -5
```

Expected: Flask and other dependencies listed.

---

### Task 3: Create .env.example and config/settings.py

**Files:**
- Create: `.env.example`
- Create: `config/settings.py`
- Create: `config/constants.py`

- [ ] **Step 1: Write .env.example**

```bash
cat > .env.example << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/logo_db
SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development
FLASK_DEBUG=1
SQLALCHEMY_ECHO=1
EOF
```

- [ ] **Step 2: Write config/settings.py**

```python
# config/settings.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-prod')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://localhost/logo_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO', False)

    # Upload settings
    UPLOAD_FOLDER = 'statics/uploads/logos'
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    # Session
    SESSION_COOKIE_SECURE = False  # Set True in production
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

    # Pagination
    ITEMS_PER_PAGE = 12

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True

class TestingConfig(Config):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config_dict = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
}

def get_config():
    env = os.getenv('FLASK_ENV', 'development')
    return config_dict.get(env, DevelopmentConfig)
```

- [ ] **Step 3: Write config/constants.py**

```python
# config/constants.py

# Logo generation defaults
ARMOIRIES_HEIGHT = 624
SPACING = 85
TEXT_SPACING = 80
FONT_SIZE = 105
LINE_SPACING = 110
TEXT_COLOR = (0, 0, 0, 255)

# Text splitting
MAX_LINES = 5
MAX_WORDS_PER_LINE = 3

# File paths
LOGO_ASSETS_PATH = 'logo_assets'
ARMOIRIES_FILE = 'armoiries.png'
LIGNE_ETAT_FILE = 'ligne_etat.png'
FONT_FILE = 'font/cooper-hewitt/CooperHewitt-Bold.otf'

# Supported languages
SUPPORTED_LANGUAGES = ['fr', 'lingala', 'swahili']

# Share link settings
SHARE_TOKEN_LENGTH = 32
SHARE_LINK_EXPIRES_DAYS = None  # None = never expires

# Institution types
INSTITUTION_TYPES = [
    'Ambassade',
    'Ministère',
    'Direction Générale',
    'Institution Autonome',
    'Établissement Public',
    'Autre'
]
```

- [ ] **Step 4: Verify files created**

```bash
cat config/settings.py | grep "class Config"
cat config/constants.py | grep "ARMOIRIES_HEIGHT"
```

Expected: Both files contain their respective content.

---

## Phase 2: Database Models & Initialization

### Task 4: Create SQLAlchemy Models (User, Template, LogoGeneration, SharedLink)

**Files:**
- Create: `models/user.py`
- Create: `models/template.py`
- Create: `models/logo.py`
- Create: `models/shared_link.py`
- Modify: `models/__init__.py`

- [ ] **Step 1: Write models/user.py**

```python
# models/user.py
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import bcrypt

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    language = db.Column(db.String(20), default='fr')  # 'fr', 'lingala', 'swahili'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    logos = db.relationship('LogoGeneration', backref='user', lazy=True, cascade='all, delete-orphan')
    created_templates = db.relationship('Template', backref='creator', lazy=True, foreign_keys='Template.created_by_admin')
    shared_links = db.relationship('SharedLink', backref='creator', lazy=True, foreign_keys='SharedLink.created_by')

    def set_password(self, password):
        """Hash password using bcrypt"""
        self.password_hash = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')

    def check_password(self, password):
        """Verify password against hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.password_hash.encode('utf-8')
        )

    def __repr__(self):
        return f'<User {self.email}>'
```

- [ ] **Step 2: Write models/template.py**

```python
# models/template.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Template(db.Model):
    __tablename__ = 'template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    institution_type = db.Column(db.String(100))
    created_by_admin = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    params = db.Column(db.JSON, default={})  # Stores generation parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    logos = db.relationship('LogoGeneration', backref='template', lazy=True)

    def get_params(self):
        """Get default parameters with fallbacks"""
        from config.constants import (
            ARMOIRIES_HEIGHT, SPACING, TEXT_SPACING, FONT_SIZE,
            LINE_SPACING, TEXT_COLOR
        )

        default_params = {
            'armoiries_height': ARMOIRIES_HEIGHT,
            'spacing': SPACING,
            'text_spacing': TEXT_SPACING,
            'font_size': FONT_SIZE,
            'line_spacing': LINE_SPACING,
            'text_color': list(TEXT_COLOR)
        }

        if self.params:
            default_params.update(self.params)

        return default_params

    def __repr__(self):
        return f'<Template {self.name}>'
```

- [ ] **Step 3: Write models/logo.py**

```python
# models/logo.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class LogoGeneration(db.Model):
    __tablename__ = 'logo_generation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    institution_name = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(20), default='fr')
    file_path_png = db.Column(db.String(500))
    file_path_jpg = db.Column(db.String(500))
    preview_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shared_links = db.relationship('SharedLink', backref='logo', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LogoGeneration {self.institution_name} by user {self.user_id}>'
```

- [ ] **Step 4: Write models/shared_link.py**

```python
# models/shared_link.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import secrets

db = SQLAlchemy()

class SharedLink(db.Model):
    __tablename__ = 'shared_link'

    id = db.Column(db.Integer, primary_key=True)
    logo_id = db.Column(db.Integer, db.ForeignKey('logo_generation.id'), nullable=False)
    token_public = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        from config.constants import SHARE_TOKEN_LENGTH
        return secrets.token_urlsafe(SHARE_TOKEN_LENGTH)

    def is_expired(self):
        """Check if share link has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def increment_view_count(self):
        """Increment view counter"""
        self.view_count += 1

    def __repr__(self):
        return f'<SharedLink {self.token_public[:8]}...>'
```

- [ ] **Step 5: Update models/__init__.py**

```python
# models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from models.user import User
from models.template import Template
from models.logo import LogoGeneration
from models.shared_link import SharedLink

db = SQLAlchemy()

__all__ = ['db', 'User', 'Template', 'LogoGeneration', 'SharedLink']
```

- [ ] **Step 6: Verify models created**

```bash
grep -l "class User\|class Template\|class LogoGeneration\|class SharedLink" models/*.py
```

Expected: All 4 model files listed.

---

### Task 5: Create init_db.py for Database Initialization

**Files:**
- Create: `init_db.py`

- [ ] **Step 1: Write init_db.py**

```python
#!/usr/bin/env python
"""
Database initialization script.
Creates all tables, indexes, and seeds default templates.

Usage:
    python init_db.py
"""

import os
import sys
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Template, LogoGeneration, SharedLink
from config.constants import INSTITUTION_TYPES

def init_database():
    """Initialize database: create tables, add seed data"""
    app = create_app()

    with app.app_context():
        print("🔧 Creating all tables...")
        db.create_all()
        print("✅ Tables created successfully")

        # Check if templates already exist
        existing_templates = Template.query.count()
        if existing_templates > 0:
            print(f"⚠️  Templates already exist ({existing_templates}). Skipping seed...")
            return

        print("\n🌱 Seeding default templates...")

        # Define default templates
        templates_data = [
            {
                'name': 'Ambassade RDC',
                'description': 'Modèle pour ambassades de la RDC à l\'étranger',
                'institution_type': 'Ambassade',
                'params': {
                    'armoiries_height': 624,
                    'spacing': 85,
                    'text_spacing': 80,
                    'font_size': 105,
                    'line_spacing': 110,
                    'text_color': [0, 0, 0, 255]
                }
            },
            {
                'name': 'Ministère Standard',
                'description': 'Modèle standard pour ministères',
                'institution_type': 'Ministère',
                'params': {
                    'armoiries_height': 624,
                    'spacing': 85,
                    'text_spacing': 80,
                    'font_size': 100,
                    'line_spacing': 110,
                    'text_color': [0, 0, 0, 255]
                }
            },
            {
                'name': 'Institution Autonome',
                'description': 'Modèle pour institutions autonomes',
                'institution_type': 'Institution Autonome',
                'params': {
                    'armoiries_height': 600,
                    'spacing': 80,
                    'text_spacing': 75,
                    'font_size': 95,
                    'line_spacing': 105,
                    'text_color': [0, 0, 0, 255]
                }
            },
            {
                'name': 'Établissement Public',
                'description': 'Modèle pour établissements publics',
                'institution_type': 'Établissement Public',
                'params': {
                    'armoiries_height': 624,
                    'spacing': 85,
                    'text_spacing': 80,
                    'font_size': 100,
                    'line_spacing': 110,
                    'text_color': [0, 0, 0, 255]
                }
            }
        ]

        for template_data in templates_data:
            template = Template(
                name=template_data['name'],
                description=template_data['description'],
                institution_type=template_data['institution_type'],
                params=template_data['params'],
                created_by_admin=None,  # Seed templates have no creator
                is_active=True
            )
            db.session.add(template)
            print(f"  ✓ Added template: {template.name}")

        db.session.commit()
        print("✅ Templates seeded successfully\n")

        # Print summary
        user_count = User.query.count()
        template_count = Template.query.count()

        print("📊 Database Summary:")
        print(f"  Users: {user_count}")
        print(f"  Templates: {template_count}")
        print("\n🚀 Database initialized successfully!")
        print("\nNext steps:")
        print("  1. Create admin user: python create_admin.py")
        print("  2. Run Flask app: python app.py")

if __name__ == '__main__':
    init_database()
```

- [ ] **Step 2: Verify init_db.py created**

```bash
head -10 init_db.py
```

Expected: File contains database initialization logic.

---

## Phase 3: Core Services

### Task 6: Create Text Splitting Algorithm (algorithms/text_splitter.py)

**Files:**
- Create: `algorithms/text_splitter.py`
- Create: `tests/test_algorithms.py`

- [ ] **Step 1: Write test file**

```python
# tests/test_algorithms.py
import pytest
from algorithms.text_splitter import split_unit_name

def test_split_single_word():
    """Test with single word input"""
    result = split_unit_name("Ambassade")
    assert result == ["AMBASSADE"]

def test_split_two_words():
    """Test with two words"""
    result = split_unit_name("Ambassade RDC")
    assert result == ["AMBASSADE", "RDC"]

def test_split_long_name():
    """Test with long name (should split with 3 words max per line after first)"""
    result = split_unit_name("Ambassade de la République Démocratique du Congo en France")
    assert len(result) <= 5
    assert result[0] == "AMBASSADE"
    assert "DE" in result[1]

def test_split_max_lines():
    """Test that output never exceeds 5 lines"""
    long_name = " ".join(["word"] * 20)
    result = split_unit_name(long_name)
    assert len(result) <= 5

def test_split_empty_string():
    """Test empty string returns empty list"""
    result = split_unit_name("")
    assert result == []

def test_split_whitespace_only():
    """Test whitespace-only string returns empty list"""
    result = split_unit_name("   ")
    assert result == []

def test_split_uppercase():
    """Test input is converted to uppercase"""
    result = split_unit_name("ambassade de france")
    assert all(line.isupper() for line in result)

def test_split_special_chars():
    """Test with special characters"""
    result = split_unit_name("Direction-Générale d'État")
    assert len(result) > 0
    assert any("DIRECTION" in line for line in result)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd /Users/moadigitalagency/marque-etat-congolais
python -m pytest tests/test_algorithms.py -v
```

Expected: All tests fail with "split_unit_name not found".

- [ ] **Step 3: Write algorithms/text_splitter.py**

```python
# algorithms/text_splitter.py
"""
Text splitting algorithm for logo generation.

Splits institution names according to these rules:
1. First line = first word only
2. Following lines = max 3 words per line
3. Maximum 5 lines total
4. All text converted to UPPERCASE
"""

def split_unit_name(nom: str, max_lines: int = 5) -> list:
    """
    Split unit/institution name into lines for logo generation.

    Args:
        nom: Institution name (any case)
        max_lines: Maximum number of lines (default 5)

    Returns:
        List of strings, each representing one line of the logo text
        Each string is UPPERCASE

    Examples:
        >>> split_unit_name("Ambassade de France")
        ['AMBASSADE', 'DE FRANCE']

        >>> split_unit_name("Ambassade de la RDC en France")
        ['AMBASSADE', 'DE LA RDC', 'EN FRANCE']
    """
    # Validate input
    if not nom or not nom.strip():
        return []

    # Convert to uppercase and split into words
    words = nom.upper().split()
    words = [w for w in words if w]  # Remove empty strings

    if not words:
        return []

    # Start with first word on first line
    lines = [words[0]]
    current_line_words = []

    # Process remaining words
    for word in words[1:]:
        current_line_words.append(word)

        # If we've reached 3 words, commit this line
        if len(current_line_words) == 3:
            lines.append(' '.join(current_line_words))
            current_line_words = []

            # Stop if we've reached max lines
            if len(lines) >= max_lines:
                break

    # Add any remaining words as final line
    if current_line_words and len(lines) < max_lines:
        lines.append(' '.join(current_line_words))

    # Return first max_lines entries
    return lines[:max_lines]
```

- [ ] **Step 4: Run tests again to verify they pass**

```bash
python -m pytest tests/test_algorithms.py -v
```

Expected: All tests PASS.

- [ ] **Step 5: Commit**

```bash
git add algorithms/text_splitter.py tests/test_algorithms.py
git commit -m "feat: add text splitting algorithm for logo names"
```

---

### Task 7: Create Logo Generator Service (services/logo_generator.py)

**Files:**
- Create: `services/logo_generator.py`
- Create: `tests/test_services.py` (partial)

- [ ] **Step 1: Write test file (partial)**

```python
# tests/test_services.py
import pytest
import os
from PIL import Image
from io import BytesIO
from services.logo_generator import LogoGeneratorService

@pytest.fixture
def logo_service():
    """Create service instance for testing"""
    return LogoGeneratorService()

def test_generate_logo_returns_bytesio(logo_service):
    """Test that generate_logo returns BytesIO object"""
    result = logo_service.generate_logo(
        unit_nom="Ambassade",
        language="fr"
    )
    assert isinstance(result, BytesIO)

def test_generate_logo_png_format(logo_service):
    """Test that output is valid PNG"""
    result = logo_service.generate_logo(
        unit_nom="Ambassade",
        language="fr"
    )
    result.seek(0)

    # Should be readable as image
    img = Image.open(result)
    assert img.format == 'PNG'
    assert img.mode == 'RGBA'  # Transparent background
```

- [ ] **Step 2: Write services/logo_generator.py**

```python
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

    def __init__(self, logo_assets_base_path: str = 'logo_assets'):
        """
        Initialize service with asset paths.

        Args:
            logo_assets_base_path: Base path to logo assets directory
        """
        self.logo_assets_base = logo_assets_base_path
        self.armoiries_path = os.path.join(logo_assets_base_path, ARMOIRIES_FILE)
        self.ligne_etat_path = os.path.join(logo_assets_base_path, LIGNE_ETAT_FILE)
        self.font_path = os.path.join(logo_assets_base_path, FONT_FILE)

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
```

- [ ] **Step 3: Run partial tests**

```bash
python -m pytest tests/test_services.py::test_generate_logo_returns_bytesio -v
```

Expected: Test should PASS (or FAIL with file not found - expected for now).

- [ ] **Step 4: Commit**

```bash
git add services/logo_generator.py tests/test_services.py
git commit -m "feat: add logo generator service with Pillow"
```

---

### Task 8: Create Auth & Template Services

**Files:**
- Create: `services/auth_service.py`
- Create: `services/template_service.py`
- Create: `services/share_service.py`
- Create: `services/i18n_service.py`

- [ ] **Step 1: Write services/auth_service.py**

```python
# services/auth_service.py
"""Authentication service for user management"""

import bcrypt
from models import db, User

class AuthService:
    """Service for authentication and user management"""

    @staticmethod
    def register_user(email: str, password: str, full_name: str = None, language: str = 'fr') -> User:
        """
        Register new user.

        Args:
            email: User email (must be unique)
            password: Plain text password (will be hashed)
            full_name: Optional full name
            language: Preferred language (default 'fr')

        Returns:
            Created User object

        Raises:
            ValueError: If email already exists
        """
        if User.query.filter_by(email=email).first():
            raise ValueError(f"User with email {email} already exists")

        user = User(
            email=email,
            full_name=full_name,
            language=language,
            role='user'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user

    @staticmethod
    def authenticate_user(email: str, password: str) -> User:
        """
        Authenticate user by email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User object if authenticated, None otherwise
        """
        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            return user

        return None

    @staticmethod
    def create_admin_user(email: str, password: str, full_name: str = 'Admin') -> User:
        """Create admin user"""
        if User.query.filter_by(email=email).first():
            raise ValueError(f"User with email {email} already exists")

        user = User(
            email=email,
            full_name=full_name,
            role='admin',
            language='fr'
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        return user
```

- [ ] **Step 2: Write services/template_service.py**

```python
# services/template_service.py
"""Template management service"""

from models import db, Template

class TemplateService:
    """Service for template CRUD operations"""

    @staticmethod
    def get_active_templates():
        """Get all active templates"""
        return Template.query.filter_by(is_active=True).all()

    @staticmethod
    def get_template_by_id(template_id: int) -> Template:
        """Get template by ID"""
        return Template.query.get(template_id)

    @staticmethod
    def create_template(
        name: str,
        description: str = None,
        institution_type: str = None,
        params: dict = None,
        created_by_admin: int = None
    ) -> Template:
        """
        Create new template.

        Args:
            name: Template name
            description: Template description
            institution_type: Type of institution
            params: Generation parameters (dict)
            created_by_admin: ID of admin who created template

        Returns:
            Created Template object
        """
        template = Template(
            name=name,
            description=description,
            institution_type=institution_type,
            params=params or {},
            created_by_admin=created_by_admin,
            is_active=True
        )

        db.session.add(template)
        db.session.commit()

        return template

    @staticmethod
    def update_template(template_id: int, **kwargs) -> Template:
        """Update template fields"""
        template = Template.query.get(template_id)

        if not template:
            raise ValueError(f"Template {template_id} not found")

        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)

        db.session.commit()

        return template

    @staticmethod
    def delete_template(template_id: int) -> bool:
        """Soft delete template (set is_active=False)"""
        template = Template.query.get(template_id)

        if not template:
            raise ValueError(f"Template {template_id} not found")

        template.is_active = False
        db.session.commit()

        return True
```

- [ ] **Step 3: Write services/share_service.py**

```python
# services/share_service.py
"""Shared link management service"""

from models import db, SharedLink, LogoGeneration
from datetime import datetime, timedelta
from config.constants import SHARE_LINK_EXPIRES_DAYS

class ShareService:
    """Service for managing public share links"""

    @staticmethod
    def create_share_link(logo_id: int, created_by: int = None, expires_days: int = None) -> SharedLink:
        """
        Create public share link for a logo.

        Args:
            logo_id: ID of logo to share
            created_by: ID of user creating share link
            expires_days: Days until link expires (None = never)

        Returns:
            SharedLink object
        """
        logo = LogoGeneration.query.get(logo_id)

        if not logo:
            raise ValueError(f"Logo {logo_id} not found")

        # Check if link already exists
        existing = SharedLink.query.filter_by(logo_id=logo_id).first()
        if existing:
            return existing

        # Calculate expiry
        expires_at = None
        if expires_days is not None:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        elif SHARE_LINK_EXPIRES_DAYS is not None:
            expires_at = datetime.utcnow() + timedelta(days=SHARE_LINK_EXPIRES_DAYS)

        share_link = SharedLink(
            logo_id=logo_id,
            token_public=SharedLink.generate_token(),
            created_by=created_by,
            expires_at=expires_at
        )

        db.session.add(share_link)
        db.session.commit()

        return share_link

    @staticmethod
    def get_share_link_by_token(token: str) -> SharedLink:
        """Get share link by token"""
        return SharedLink.query.filter_by(token_public=token).first()

    @staticmethod
    def is_share_link_valid(share_link: SharedLink) -> bool:
        """Check if share link is valid and not expired"""
        if not share_link:
            return False

        return not share_link.is_expired()

    @staticmethod
    def record_share_view(share_link: SharedLink):
        """Record that share link was viewed"""
        share_link.increment_view_count()
        db.session.commit()
```

- [ ] **Step 4: Write services/i18n_service.py**

```python
# services/i18n_service.py
"""Internationalization (i18n) service"""

import json
import os
from config.constants import SUPPORTED_LANGUAGES

class I18nService:
    """Service for managing translations"""

    _translations = {}

    @classmethod
    def load_translations(cls):
        """Load all translation files"""
        lang_dir = 'lang'

        for lang in SUPPORTED_LANGUAGES:
            lang_file = os.path.join(lang_dir, f'{lang}.json')

            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    cls._translations[lang] = json.load(f)
            else:
                cls._translations[lang] = {}

    @classmethod
    def get_text(cls, key: str, language: str = 'fr', default: str = None) -> str:
        """
        Get translated text by key.

        Args:
            key: Translation key (e.g., 'common.welcome')
            language: Language code
            default: Default text if key not found

        Returns:
            Translated text or default value
        """
        if not cls._translations:
            cls.load_translations()

        if language not in cls._translations:
            return default or key

        # Navigate nested keys (e.g., 'common.welcome' → translations['common']['welcome'])
        keys = key.split('.')
        value = cls._translations[language]

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default or key

    # Jinja2 template filter
    @staticmethod
    def jinja_filter(key: str, language: str = 'fr') -> str:
        """Jinja2 filter for translations in templates"""
        return I18nService.get_text(key, language)
```

- [ ] **Step 5: Create services/__init__.py**

```python
# services/__init__.py
from services.logo_generator import LogoGeneratorService
from services.auth_service import AuthService
from services.template_service import TemplateService
from services.share_service import ShareService
from services.i18n_service import I18nService

__all__ = [
    'LogoGeneratorService',
    'AuthService',
    'TemplateService',
    'ShareService',
    'I18nService'
]
```

- [ ] **Step 6: Commit**

```bash
git add services/
git commit -m "feat: add all service layers (auth, template, share, i18n)"
```

---

## Phase 4: Flask App & Routes (Tasks 9-14)

[CONTINUING IN NEXT MESSAGE - TOO LONG]

Due to length, I'll save the plan and continue with the remaining phases in the next part.

- [ ] **Checkpoint: Review Phase 1-3 completion before proceeding to Phase 4 (Routes)**

---

**Plan File Saved:** `/Users/moadigitalagency/marque-etat-congolais/docs/superpowers/plans/2026-03-26-logo-generator-implementation.md`

This is **Part 1 of 2** of the implementation plan. Phase 4 (Routes), Phase 5 (Templates), Phase 6 (Frontend JS), and final testing will be in the continuation.

Would you like me to:
1. **Continue with remaining phases (4-6)** in the same file?
2. **Proceed to execution** of Phase 1-3 first (setup, models, services)?

Recommend: **Option 2** - Let's implement Phase 1-3 first, test it, then add routes/templates.
