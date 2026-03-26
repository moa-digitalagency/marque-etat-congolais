# routes/api.py
"""
API routes blueprint.
Provides JSON endpoints for frontend AJAX calls.
Includes template listing and user logo management.
"""

from flask import Blueprint, request, jsonify, url_for, current_app
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
import traceback

from models import db, LogoGeneration, SharedLink, Template
from services import TemplateService

api_bp = Blueprint('api', __name__, url_prefix='/api')


@api_bp.route('/templates', methods=['GET'])
def list_templates():
    """
    List all active templates.
    No login required (public endpoint).

    Returns:
        JSON array of templates with id, name, description, institution_type, params
        Example: [{"id": 1, "name": "Ambassade RDC", "description": "...", "institution_type": "Ambassade", "params": {...}}, ...]
    """
    try:
        # Get all active templates using service
        templates = TemplateService.get_active_templates()

        # Build response
        templates_data = []
        for template in templates:
            templates_data.append({
                'id': template.id,
                'name': template.name,
                'description': template.description or '',
                'institution_type': template.institution_type or '',
                'params': template.params or {}
            })

        return jsonify(templates_data), 200

    except ValueError as e:
        current_app.logger.error(f'Erreur service templates: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur lors de la récupération des templates'}), 500
    except Exception as e:
        current_app.logger.error(f'Erreur inattendue: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500


@api_bp.route('/logos', methods=['GET'])
@login_required
def list_logos():
    """
    List user's generated logos with pagination.
    Requires login.

    Query parameters:
        page (int, default 1): Current page number
        per_page (int, default 20, max 100): Items per page

    Returns:
        JSON with pagination info and logos array
        Example: {"total": 42, "pages": 3, "current_page": 1, "per_page": 20, "logos": [...]}
        Each logo includes: id, institution_name, template_id, template_name, language,
                          preview_url, png_url, jpg_url, created_at, has_share_link
    """
    try:
        # Get pagination parameters with validation
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
        except ValueError:
            return jsonify({'error': 'Paramètres de pagination invalides'}), 400

        # Validate pagination values
        if page < 1:
            return jsonify({'error': 'Le numéro de page doit être >= 1'}), 400

        if per_page < 1 or per_page > 100:
            return jsonify({'error': 'per_page doit être entre 1 et 100'}), 400

        # Query user's logos with eager-loaded template and shared_links relationships
        # Order by created_at DESC (newest first)
        query = LogoGeneration.query.filter_by(user_id=current_user.id) \
            .options(db.joinedload(LogoGeneration.template), db.joinedload(LogoGeneration.shared_links)) \
            .order_by(desc(LogoGeneration.created_at))

        # Paginate results
        paginated = query.paginate(page=page, per_page=per_page, error_out=False)

        # Build logos data
        logos_data = []
        for logo in paginated.items:
            # Check if logo has any non-expired share link
            has_share = any(
                sl for sl in logo.shared_links
                if not sl.is_expired()
            )

            logos_data.append({
                'id': logo.id,
                'institution_name': logo.institution_name,
                'template_id': logo.template_id,
                'template_name': logo.template.name if logo.template else '',
                'language': logo.language,
                'png_url': url_for('public.download', logo_id=logo.id, format='png', _external=False),
                'jpg_url': url_for('public.download', logo_id=logo.id, format='jpg', _external=False),
                'created_at': logo.created_at.isoformat(),
                'has_share_link': has_share
            })

        # Build response with pagination info
        response = {
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page,
            'per_page': per_page,
            'logos': logos_data
        }

        return jsonify(response), 200

    except SQLAlchemyError as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur base de données: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur base de données'}), 500
    except Exception as e:
        current_app.logger.error(f'Erreur inattendue: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500
