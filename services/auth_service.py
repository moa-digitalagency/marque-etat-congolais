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
