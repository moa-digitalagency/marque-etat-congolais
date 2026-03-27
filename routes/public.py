# routes/public.py
"""
Public routes blueprint.
Handles logo generation, sharing, and public access to shared logos.
"""

import os
import uuid
import traceback
from datetime import datetime
from io import BytesIO

from flask import (
    Blueprint, request, jsonify, render_template,
    send_file, current_app, url_for, flash, redirect
)
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from models import db, LogoGeneration, SharedLink, Template
from services import LogoGeneratorService, ShareService, TemplateService
from algorithms.text_splitter import split_unit_name, split_unit_name_ambassade

public_bp = Blueprint('public', __name__, template_folder='../templates')


@public_bp.route('/generate', methods=['GET'])
@login_required
def generate():
    """
    Display logo generation form with template selector, institution name input,
    language selector, and live preview.
    """
    try:
        # Get all active templates
        templates = Template.query.filter_by(is_active=True).all()

        if not templates:
            flash('Aucun modèle disponible pour la génération de logos', 'error')
            return redirect(url_for('dashboard.index'))

        return render_template(
            'public/generate.html',
            templates=templates,
            current_user=current_user
        )

    except FileNotFoundError as e:
        flash('Fichier template manquant', 'error')
        return redirect(url_for('dashboard.index'))
    except Exception as e:
        current_app.logger.error(f'Erreur inattendue dans generate: {traceback.format_exc()}')
        flash('Erreur serveur lors du chargement de la page', 'error')
        return redirect(url_for('dashboard.index'))


@public_bp.route('/api/generate', methods=['POST'])
@login_required
def api_generate():
    """
    AJAX endpoint for logo generation.

    Accepts JSON: {template_id, institution_name, language}
    Returns JSON: {preview_url, png_url, jpg_url, logo_id} or error response
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400

        # Validate required fields
        template_id = data.get('template_id')
        institution_name = data.get('institution_name', '').strip()
        language = data.get('language', 'fr')

        if not template_id:
            return jsonify({'error': 'ID du modèle requis'}), 400

        if not institution_name:
            return jsonify({'error': 'Nom de l\'institution requis'}), 400

        # Validate template exists
        template = Template.query.get(template_id)
        if not template or not template.is_active:
            return jsonify({'error': 'Modèle non trouvé ou inactif'}), 404

        # Validate language
        if language not in ['fr', 'lingala', 'swahili']:
            language = 'fr'

        # Validate institution name is not empty after stripping
        # Use model-specific text splitting function if available
        if template.name == 'Ambassade RDC':
            text_lines = split_unit_name_ambassade(institution_name)
        else:
            text_lines = split_unit_name(institution_name)

        if not text_lines:
            return jsonify({'error': 'Le nom de l\'institution est vide ou invalide'}), 400

        # Generate logo
        try:
            logo_generator = LogoGeneratorService()
            template_params = template.get_params()

            # Generate PNG
            png_buffer = logo_generator.generate_logo(
                unit_nom=institution_name,
                language=language,
                armoiries_height=template_params.get('armoiries_height'),
                spacing=template_params.get('spacing'),
                text_spacing=template_params.get('text_spacing'),
                font_size=template_params.get('font_size'),
                line_spacing=template_params.get('line_spacing'),
                text_color=tuple(template_params.get('text_color', [0, 0, 0, 255])),
                template_name=template.name
            )

            # Generate PNG White (white version)
            png_white_buffer = logo_generator.generate_logo_white(
                unit_nom=institution_name,
                language=language,
                armoiries_height=template_params.get('armoiries_height'),
                spacing=template_params.get('spacing'),
                text_spacing=template_params.get('text_spacing'),
                font_size=template_params.get('font_size'),
                line_spacing=template_params.get('line_spacing'),
                template_name=template.name
            )

            # Generate JPG
            jpg_buffer = logo_generator.convert_png_to_jpg(png_buffer)

        except FileNotFoundError as e:
            return jsonify({'error': f'Fichier asset manquant: {str(e)}'}), 500
        except ValueError as e:
            return jsonify({'error': f'Erreur validation: {str(e)}'}), 400
        except Exception as e:
            current_app.logger.error(f'Erreur génération logo: {traceback.format_exc()}')
            return jsonify({'error': 'Erreur lors de la génération du logo'}), 500

        # Create uploads directory if it doesn't exist
        upload_folder = current_app.config.get('UPLOAD_FOLDER', 'statics/uploads/logos')
        os.makedirs(upload_folder, exist_ok=True)

        # Create database record FIRST (without files) - defer file writes until after flush
        logo = LogoGeneration(
            user_id=current_user.id,
            template_id=template_id,
            institution_name=institution_name,
            language=language,
            file_path_png='',  # Will be set after flush
            file_path_png_white='',  # Will be set after flush
            file_path_jpg='',  # Will be set after flush
            preview_url=''  # Will be set after flush
        )

        db.session.add(logo)
        db.session.flush()  # Generate logo.id without committing

        # Now write files using the generated logo.id
        try:
            timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
            filename_base = f"{logo.id}_{timestamp}"

            # Save PNG
            png_filename = f"{filename_base}.png"
            png_path = os.path.join(upload_folder, png_filename)
            with open(png_path, 'wb') as f:
                png_buffer.seek(0)
                f.write(png_buffer.read())

            # Save PNG White
            png_white_filename = f"{filename_base}_white.png"
            png_white_path = os.path.join(upload_folder, png_white_filename)
            with open(png_white_path, 'wb') as f:
                png_white_buffer.seek(0)
                f.write(png_white_buffer.read())

            # Save JPG
            jpg_filename = f"{filename_base}.jpg"
            jpg_path = os.path.join(upload_folder, jpg_filename)
            with open(jpg_path, 'wb') as f:
                jpg_buffer.seek(0)
                f.write(jpg_buffer.read())

            # Update logo with file paths
            logo.file_path_png = png_path
            logo.file_path_png_white = png_white_path
            logo.file_path_jpg = jpg_path
            logo.preview_url = url_for('public.download', logo_id=logo.id, format='png', _external=False)

            db.session.commit()

        except IOError as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur écriture fichier: {traceback.format_exc()}')
            return jsonify({'error': 'Erreur lors de l\'enregistrement des fichiers'}), 500
        except IntegrityError as e:
            db.session.rollback()
            current_app.logger.error(f'Erreur base de données: {traceback.format_exc()}')
            return jsonify({'error': 'Erreur lors de l\'enregistrement en base de données'}), 500

        # Return response
        return jsonify({
            'logo_id': logo.id,
            'preview_url': url_for('public.download', logo_id=logo.id, format='png', _external=False),
            'png_url': url_for('public.download', logo_id=logo.id, format='png', _external=False),
            'png_white_url': url_for('public.download', logo_id=logo.id, format='png_white', _external=False),
            'jpg_url': url_for('public.download', logo_id=logo.id, format='jpg', _external=False),
            'created_at': logo.created_at.isoformat()
        }), 200

    except ValueError as e:
        return jsonify({'error': f'Erreur validation: {str(e)}'}), 400
    except Exception as e:
        current_app.logger.error(f'Erreur inattendue api_generate: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500


@public_bp.route('/share/<token>', methods=['GET'])
def share(token):
    """
    Display publicly shared logo without requiring login.
    Show logo image and download buttons.
    """
    try:
        # Lookup SharedLink by token
        share_link = ShareService.get_share_link_by_token(token)

        if not share_link:
            return render_template('public/share_not_found.html'), 404

        # Check if link is expired
        if not ShareService.is_share_link_valid(share_link):
            return render_template('public/share_expired.html'), 410

        # Increment view count
        ShareService.record_share_view(share_link)

        # Get the logo
        logo = share_link.logo

        if not logo:
            return render_template('public/share_not_found.html'), 404

        return render_template(
            'public/share.html',
            logo=logo,
            share_link=share_link,
            png_url=url_for('public.download', logo_id=logo.id, format='png', _external=False),
            png_white_url=url_for('public.download', logo_id=logo.id, format='png_white', _external=False),
            jpg_url=url_for('public.download', logo_id=logo.id, format='jpg', _external=False)
        )

    except FileNotFoundError as e:
        current_app.logger.warning(f'Ressource partagée non trouvée: {str(e)}')
        return render_template('public/share_error.html', error='Ressource non disponible'), 404
    except Exception as e:
        current_app.logger.error(f'Erreur inattendue share: {traceback.format_exc()}')
        return render_template('public/share_error.html', error='Erreur serveur'), 500


@public_bp.route('/api/share', methods=['POST'])
@login_required
def api_share():
    """
    Create shareable link for a logo.

    Accepts JSON: {logo_id}
    Returns JSON: {share_token, share_url}
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Données JSON requises'}), 400

        logo_id = data.get('logo_id')

        if not logo_id:
            return jsonify({'error': 'ID du logo requis'}), 400

        # Verify logo exists and belongs to current user
        logo = LogoGeneration.query.get(logo_id)

        if not logo:
            return jsonify({'error': 'Logo non trouvé'}), 404

        if logo.user_id != current_user.id:
            return jsonify({'error': 'Vous n\'avez pas l\'autorisation de partager ce logo'}), 403

        # Create share link using ShareService
        try:
            share_link = ShareService.create_share_link(
                logo_id=logo_id,
                created_by=current_user.id
            )

            share_url = url_for(
                'public.share',
                token=share_link.token_public,
                _external=True
            )

            return jsonify({
                'share_token': share_link.token_public,
                'share_url': share_url,
                'expires_at': share_link.expires_at.isoformat() if share_link.expires_at else None
            }), 200

        except ValueError as e:
            return jsonify({'error': str(e)}), 400

    except Exception as e:
        return jsonify({'error': f'Erreur serveur: {str(e)}'}), 500


@public_bp.route('/download/<int:logo_id>', methods=['GET'])
def download(logo_id):
    """
    Download logo file.

    Query parameter: format=png|png_white|jpg (default: png)
    """
    try:
        format_type = request.args.get('format', 'png').lower()

        if format_type not in ['png', 'png_white', 'jpg']:
            return jsonify({'error': 'Format invalide. Utilisez png, png_white ou jpg'}), 400

        # Get logo
        logo = LogoGeneration.query.get(logo_id)

        if not logo:
            return jsonify({'error': 'Logo non trouvé'}), 404

        # Determine file path based on format
        if format_type == 'png':
            file_path = logo.file_path_png
            mimetype = 'image/png'
        elif format_type == 'png_white':
            file_path = logo.file_path_png_white
            mimetype = 'image/png'
        else:  # jpg
            file_path = logo.file_path_jpg
            mimetype = 'image/jpeg'

        # Verify file exists
        if not file_path or not os.path.exists(file_path):
            return jsonify({'error': 'Fichier de logo non trouvé'}), 404

        # Security: Validate file path is within upload folder (prevent path traversal)
        upload_folder = os.path.abspath(current_app.config.get('UPLOAD_FOLDER', 'statics/uploads/logos'))
        file_full_path = os.path.abspath(file_path)

        if not file_full_path.startswith(upload_folder):
            current_app.logger.warning(f'Tentative path traversal détectée: {file_full_path}')
            return jsonify({'error': 'Accès refusé'}), 403

        # Send file
        if format_type == 'png_white':
            download_name = f"logo_{logo.id}_white.png"
        else:
            download_name = f"logo_{logo.id}.{format_type}"

        return send_file(
            file_full_path,
            mimetype=mimetype,
            as_attachment=True,
            download_name=download_name
        )

    except FileNotFoundError as e:
        return jsonify({'error': 'Fichier non trouvé'}), 404
    except IOError as e:
        current_app.logger.error(f'Erreur lecture fichier: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur lors du téléchargement du fichier'}), 500
    except Exception as e:
        current_app.logger.error(f'Erreur inattendue download: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500
