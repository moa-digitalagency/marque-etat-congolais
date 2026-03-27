# models/logo.py
from datetime import datetime
from models.database import db

class LogoGeneration(db.Model):
    __tablename__ = 'logo_generation'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    template_id = db.Column(db.Integer, db.ForeignKey('template.id'), nullable=False)
    institution_name = db.Column(db.String(255), nullable=False)
    language = db.Column(db.String(20), default='fr')
    file_path_png = db.Column(db.String(500))
    file_path_png_white = db.Column(db.String(500))
    file_path_jpg = db.Column(db.String(500))
    preview_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    shared_links = db.relationship('SharedLink', backref='logo', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<LogoGeneration {self.institution_name} by user {self.user_id}>'
