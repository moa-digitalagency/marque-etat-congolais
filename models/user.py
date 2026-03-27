# models/user.py
from flask_login import UserMixin
from datetime import datetime
import bcrypt
from models.database import db

class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(255))
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    language = db.Column(db.String(20), default='fr')  # 'fr', 'lingala', 'swahili'
    ministry = db.Column(db.String(255), nullable=True)  # Ministry/department name
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
