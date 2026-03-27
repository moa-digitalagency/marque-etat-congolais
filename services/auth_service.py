# services/auth_service.py
"""Authentication service for user management"""

import bcrypt
from models import db, User

class AuthService:
    """Service for authentication and user management"""

    @staticmethod
    def register_user(email, password, full_name=None, language='fr', role='user'):
        """Register a new user with validation"""
        from models.user import User
        import re

        # Email validation
        if not email or not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
            raise ValueError('Email invalide')

        if User.query.filter_by(email=email).first():
            raise ValueError(f'Un utilisateur avec l\'email {email} existe déjà')

        if not password or len(password) < 6:
            raise ValueError('Le mot de passe doit contenir au moins 6 caractères')

        if role not in ['user', 'admin']:
            raise ValueError('Rôle invalide')

        if language not in ['fr', 'lingala', 'swahili']:
            raise ValueError('Langue non supportée')

        user = User(email=email, full_name=full_name, language=language, role=role)
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
