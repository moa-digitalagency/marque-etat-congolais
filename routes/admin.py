# routes/admin.py
"""
Admin routes blueprint.
Handles admin panel routes for user management and system administration.
"""

from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from models import db, User

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
    """
    Admin user management page.
    Displays all users in a table format with edit/delete capabilities.
    """
    # Get all users
    all_users = User.query.order_by(User.created_at.desc()).all()

    return render_template(
        'admin/users.html',
        users=all_users,
        total_users=len(all_users)
    )
