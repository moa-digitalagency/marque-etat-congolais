# routes/dashboard.py
"""
Dashboard routes blueprint.
Handles user dashboard, logo history, logo details, and logo deletion.
"""

import os
import traceback
from flask import (
    Blueprint, render_template, request, jsonify, redirect, url_for,
    flash, current_app, abort
)
from flask_login import login_required, current_user
from sqlalchemy import desc
from sqlalchemy.exc import SQLAlchemyError
from models import db, LogoGeneration, SharedLink

# Configuration constants
MAX_PER_PAGE = 100

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('', methods=['GET'])
@dashboard_bp.route('/', methods=['GET'])
@login_required
def index():
    """
    Dashboard home page.
    Shows welcome message with user's full_name.
    Shows stats: total logos generated, recent logos.
    Shows quick links to generate, view history.
    """
    try:
        # Get user stats
        total_logos = LogoGeneration.query.filter_by(user_id=current_user.id).count()

        # Get recent logos (last 3)
        recent_logos = LogoGeneration.query.filter_by(user_id=current_user.id) \
            .order_by(desc(LogoGeneration.created_at)) \
            .limit(3) \
            .all()

        return render_template(
            'dashboard/home.html',
            user=current_user,
            total_logos=total_logos,
            recent_logos=recent_logos
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error(f'Erreur base de données: {traceback.format_exc()}')
        flash('Erreur lors du chargement du tableau de bord', 'error')
        return redirect(url_for('public.generate'))
    except Exception:
        current_app.logger.error(f'Erreur inattendue: {traceback.format_exc()}')
        flash('Erreur serveur', 'error')
        return redirect(url_for('public.generate'))


@dashboard_bp.route('/history', methods=['GET'])
@login_required
def history():
    """
    Logo history with pagination.
    Query parameters: page (default 1), per_page (default 20)
    Filters to current_user.id only.
    Order by created_at DESC (newest first).
    Eager load template relationship (no N+1 queries).
    """
    try:
        # Get pagination parameters with validation
        try:
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
        except ValueError:
            page = 1
            per_page = 20

        # Validate pagination values
        if page < 1:
            page = 1

        if per_page < 1 or per_page > MAX_PER_PAGE:
            per_page = 20

        # Query user's logos with eager-loaded template relationship
        # Order by created_at DESC (newest first)
        query = LogoGeneration.query.filter_by(user_id=current_user.id) \
            .options(db.joinedload(LogoGeneration.template)) \
            .order_by(desc(LogoGeneration.created_at))

        # Paginate results
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return render_template(
            'dashboard/history.html',
            logos=pagination.items,
            pagination=pagination,
            page=page,
            per_page=per_page
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error(f'Erreur base de données: {traceback.format_exc()}')
        flash('Erreur lors du chargement de l\'historique', 'error')
        return redirect(url_for('dashboard.index'))
    except Exception:
        current_app.logger.error(f'Erreur inattendue: {traceback.format_exc()}')
        flash('Erreur serveur', 'error')
        return redirect(url_for('dashboard.index'))


@dashboard_bp.route('/logo/<int:logo_id>', methods=['GET'])
@login_required
def logo_detail(logo_id):
    """
    Logo details page.
    Verify logo belongs to current_user (403 if not owner).
    Load logo with template details.
    Show full logo image, details, download options.
    """
    try:
        # Get logo with template
        logo = LogoGeneration.query \
            .options(db.joinedload(LogoGeneration.template)) \
            .filter_by(id=logo_id, user_id=current_user.id) \
            .first()

        # Check if logo exists and belongs to current user
        if not logo:
            abort(404)

        return render_template(
            'dashboard/logo_detail.html',
            logo=logo
        )

    except SQLAlchemyError:
        db.session.rollback()
        current_app.logger.error(f'Erreur base de données: {traceback.format_exc()}')
        abort(500)
    except Exception:
        current_app.logger.error(f'Erreur inattendue: {traceback.format_exc()}')
        abort(500)


@dashboard_bp.route('/<int:logo_id>', methods=['DELETE'])
@login_required
def delete_logo(logo_id):
    """
    Delete a logo.
    Accepts JSON or form data.
    Verify logo belongs to current_user (403 if not owner).
    Delete associated SharedLink records (cascade).
    Delete logo files from disk (PNG and JPG).
    Delete LogoGeneration record from database.
    Returns JSON response: {"success": true, "message": "..."}
    Status code: 200 on success, 403 on unauthorized, 404 on not found.
    """
    current_app.logger.info(f'DELETE request received for logo {logo_id} from user {current_user.id}')
    try:
        # Get logo record
        logo = LogoGeneration.query.filter_by(id=logo_id, user_id=current_user.id).first()
        current_app.logger.info(f'Logo found: {logo is not None}')

        # Check if logo exists and belongs to current user
        if not logo:
            return jsonify({'success': False, 'error': 'Logo non trouvé'}), 404

        # Delete files from disk if they exist
        try:
            # Delete PNG file
            if logo.file_path_png:
                png_path = logo.file_path_png
                # If path is not absolute, join with UPLOAD_FOLDER
                if not os.path.isabs(png_path):
                    png_path = os.path.join(current_app.config['UPLOAD_FOLDER'], png_path)
                if os.path.exists(png_path):
                    os.remove(png_path)
                    current_app.logger.info(f'Fichier PNG supprimé: {png_path}')

            # Delete JPG file
            if logo.file_path_jpg:
                jpg_path = logo.file_path_jpg
                # If path is not absolute, join with UPLOAD_FOLDER
                if not os.path.isabs(jpg_path):
                    jpg_path = os.path.join(current_app.config['UPLOAD_FOLDER'], jpg_path)
                if os.path.exists(jpg_path):
                    os.remove(jpg_path)
                    current_app.logger.info(f'Fichier JPG supprimé: {jpg_path}')

        except OSError:
            current_app.logger.error(f'Erreur lors de la suppression des fichiers: {traceback.format_exc()}')
            # Don't fail the deletion if file cleanup fails - files might already be deleted

        # Delete from database
        # SharedLinks will be automatically deleted due to cascade on LogoGeneration.shared_links
        try:
            db.session.delete(logo)
            db.session.commit()
            current_app.logger.info(f'Logo {logo_id} supprimé par utilisateur {current_user.id}')

            return jsonify({
                'success': True,
                'message': 'Logo supprimé avec succès'
            }), 200

        except SQLAlchemyError:
            db.session.rollback()
            current_app.logger.error(f'Erreur base de données lors de la suppression: {traceback.format_exc()}')
            return jsonify({
                'success': False,
                'error': 'Erreur lors de la suppression du logo'
            }), 500

    except Exception:
        current_app.logger.error(f'Erreur inattendue: {traceback.format_exc()}')
        return jsonify({
            'success': False,
            'error': 'Erreur serveur'
        }), 500
