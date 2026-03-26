# routes/auth.py
"""
Authentication routes blueprint.
Handles user login, registration, logout, and profile management.
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from services import AuthService

auth_bp = Blueprint('auth', __name__, template_folder='../templates')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return redirect(url_for('auth.login'))

        user = AuthService.authenticate_user(email, password)

        if user:
            login_user(user)
            flash(f'Bienvenue {user.email}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Email ou mot de passe incorrect', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration route"""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        full_name = request.form.get('full_name')
        language = request.form.get('language', 'fr')

        # Validation
        if not email or not password:
            flash('Email et mot de passe requis', 'error')
            return redirect(url_for('auth.register'))

        if password != password_confirm:
            flash('Les mots de passe ne correspondent pas', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 6:
            flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
            return redirect(url_for('auth.register'))

        try:
            user = AuthService.register_user(
                email=email,
                password=password,
                full_name=full_name,
                language=language
            )
            flash('Compte créé avec succès! Veuillez vous connecter.', 'success')
            return redirect(url_for('auth.login'))

        except ValueError as e:
            flash(str(e), 'error')

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Logout route"""
    logout_user()
    flash('Vous avez été déconnecté.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile route"""
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        language = request.form.get('language')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        new_password_confirm = request.form.get('new_password_confirm')

        # Update basic info
        if full_name:
            current_user.full_name = full_name

        if language:
            current_user.language = language

        # Update password if provided
        if new_password:
            if not current_password:
                flash('Mot de passe actuel requis pour changer le mot de passe', 'error')
                return redirect(url_for('auth.profile'))

            if not current_user.check_password(current_password):
                flash('Mot de passe actuel incorrect', 'error')
                return redirect(url_for('auth.profile'))

            if new_password != new_password_confirm:
                flash('Les nouveaux mots de passe ne correspondent pas', 'error')
                return redirect(url_for('auth.profile'))

            if len(new_password) < 6:
                flash('Le mot de passe doit contenir au moins 6 caractères', 'error')
                return redirect(url_for('auth.profile'))

            current_user.set_password(new_password)

        # Save changes
        from models import db
        db.session.commit()
        flash('Profil mis à jour avec succès', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
