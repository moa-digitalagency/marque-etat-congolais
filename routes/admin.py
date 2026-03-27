# routes/admin.py
"""
Admin routes blueprint.
Handles admin panel routes for user management and system administration.
"""

from functools import wraps
from datetime import datetime, timedelta
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, User
from models.logo import LogoGeneration
from services.auth_service import AuthService

admin_bp = Blueprint('admin', __name__, template_folder='../templates')


def admin_required(f):
    """
    Decorator to check if user is an admin.
    Redirects non-admin users to dashboard with an error message.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Vous n\'avez pas accès à cette page.', 'error')
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function


@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_required
def users():
    """Display user management page"""
    all_users = User.query.order_by(User.created_at.desc()).all()

    # Calculate stats
    total_users = len(all_users)
    admin_count = sum(1 for u in all_users if u.role == 'admin')
    user_count = total_users - admin_count
    active_users = sum(1 for u in all_users if u.is_active)
    inactive_users = total_users - active_users

    return render_template('admin/users.html',
        users=all_users,
        current_user=current_user,
        total_users=total_users,
        admin_count=admin_count,
        user_count=user_count,
        active_users=active_users,
        inactive_users=inactive_users
    )


@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@admin_required
def create_user():
    """
    Create new user page and form handler.
    GET: Display the user creation form.
    POST: Handle form submission and create new user.
    """
    if request.method == 'POST':
        # Get form data
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()
        full_name = request.form.get('full_name', '').strip()
        role = request.form.get('role', 'user').strip()

        # Validation
        errors = []

        if not email:
            errors.append('Email est requis.')
        if not password:
            errors.append('Mot de passe est requis.')
        if len(password) < 6:
            errors.append('Mot de passe doit contenir au moins 6 caractères.')
        if password != password_confirm:
            errors.append('Les mots de passe ne correspondent pas.')
        if role not in ['user', 'admin']:
            errors.append('Rôle invalide.')

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('admin/create_user.html')

        # Try to create user
        try:
            AuthService.register_user(
                email=email,
                password=password,
                full_name=full_name if full_name else None,
                role=role
            )
            flash(f'Utilisateur {email} créé avec succès.', 'success')
            return redirect(url_for('admin.users'))
        except ValueError as e:
            flash(str(e), 'error')
            return render_template('admin/create_user.html')

    return render_template('admin/create_user.html')


@admin_bp.route('/users/<int:user_id>/profile')
@login_required
@admin_required
def user_profile(user_id):
    """Display user profile and statistics"""
    user = User.query.get_or_404(user_id)

    # Get stats
    total_logos = LogoGeneration.query.filter_by(user_id=user_id).count()

    # Logos this month
    first_day_of_month = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    logos_this_month = LogoGeneration.query.filter(
        LogoGeneration.user_id == user_id,
        LogoGeneration.created_at >= first_day_of_month
    ).count()

    # Recent logos
    recent_logos = LogoGeneration.query.filter_by(user_id=user_id).order_by(
        LogoGeneration.created_at.desc()
    ).limit(10).all()

    # Last logo date
    last_logo = LogoGeneration.query.filter_by(user_id=user_id).order_by(
        LogoGeneration.created_at.desc()
    ).first()
    last_logo_date = last_logo.created_at.strftime('%d %b %Y') if last_logo else None

    return render_template('admin/user_profile.html',
        user=user,
        total_logos=total_logos,
        logos_this_month=logos_this_month,
        last_logo_date=last_logo_date,
        recent_logos=recent_logos
    )
