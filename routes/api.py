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

from models import db, LogoGeneration, SharedLink, Template, User
from services import TemplateService
from services.auth_service import AuthService

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


@api_bp.route('/admin/users', methods=['POST'])
@login_required
def create_user():
    """Create a new user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403

    data = request.get_json()

    # Validate required fields
    email = data.get('email', '').strip()
    password = data.get('password', '').strip()

    if not email:
        return jsonify({'error': 'Email est requis'}), 400

    if not password or len(password) < 6:
        return jsonify({'error': 'Mot de passe doit contenir au moins 6 caractères'}), 400

    try:
        # Create user using AuthService
        user = AuthService.register_user(
            email=email,
            password=password,
            full_name=data.get('full_name', '').strip() or None,
            role=data.get('role', 'user')
        )

        # Update ministry if provided
        if data.get('ministry'):
            user.ministry = data.get('ministry').strip()
            db.session.commit()

        return jsonify({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'ministry': user.ministry,
            'role': user.role,
            'is_active': user.is_active
        }), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur création utilisateur: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500


@api_bp.route('/admin/users/<int:user_id>', methods=['POST'])
@login_required
def update_user(user_id):
    """Update user details (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403

    user = User.query.get_or_404(user_id)
    data = request.get_json()

    try:
        if 'role' in data:
            if data['role'] not in ['user', 'admin']:
                return jsonify({'error': 'Rôle invalide'}), 400
            user.role = data['role']

        if 'is_active' in data:
            user.is_active = data['is_active']

        if 'full_name' in data:
            user.full_name = data['full_name'] if data['full_name'] else None

        if 'ministry' in data:
            user.ministry = data['ministry'] if data['ministry'] else None

        if 'password' in data and data['password']:
            # Update password using the service
            AuthService.update_password(user, data['password'])

        db.session.commit()

        return jsonify({
            'id': user.id,
            'email': user.email,
            'full_name': user.full_name,
            'ministry': user.ministry,
            'role': user.role,
            'is_active': user.is_active
        })
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur mise à jour utilisateur: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500


@api_bp.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    """Delete a user (admin only)"""
    if current_user.role != 'admin':
        return jsonify({'error': 'Accès refusé'}), 403

    if user_id == current_user.id:
        return jsonify({'error': 'Vous ne pouvez pas supprimer votre propre compte'}), 400

    try:
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Utilisateur supprimé avec succès'}), 200
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f'Erreur suppression utilisateur: {traceback.format_exc()}')
        return jsonify({'error': 'Erreur serveur'}), 500
