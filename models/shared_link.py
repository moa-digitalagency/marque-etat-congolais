# models/shared_link.py
from datetime import datetime
import secrets
from models.database import db

class SharedLink(db.Model):
    __tablename__ = 'shared_link'

    id = db.Column(db.Integer, primary_key=True)
    logo_id = db.Column(db.Integer, db.ForeignKey('logo_generation.id'), nullable=False)
    token_public = db.Column(db.String(255), unique=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    view_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @staticmethod
    def generate_token():
        """Generate a secure random token"""
        from config.constants import SHARE_TOKEN_LENGTH
        return secrets.token_urlsafe(SHARE_TOKEN_LENGTH)

    def is_expired(self):
        """Check if share link has expired"""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    def increment_view_count(self):
        """Increment view counter"""
        self.view_count += 1

    def __repr__(self):
        return f'<SharedLink {self.token_public[:8]}...>'
