# models/template.py
from datetime import datetime
import json
from models.database import db

class Template(db.Model):
    __tablename__ = 'template'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    institution_type = db.Column(db.String(100))
    created_by_admin = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    params = db.Column(db.JSON, default={})  # Stores generation parameters
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Relationships
    logos = db.relationship('LogoGeneration', backref='template', lazy=True)

    def get_params(self):
        """Get default parameters with fallbacks"""
        from config.constants import (
            ARMOIRIES_HEIGHT, SPACING, TEXT_SPACING, FONT_SIZE,
            LINE_SPACING, TEXT_COLOR
        )

        default_params = {
            'armoiries_height': ARMOIRIES_HEIGHT,
            'spacing': SPACING,
            'text_spacing': TEXT_SPACING,
            'font_size': FONT_SIZE,
            'line_spacing': LINE_SPACING,
            'text_color': list(TEXT_COLOR)
        }

        if self.params:
            default_params.update(self.params)

        return default_params

    def __repr__(self):
        return f'<Template {self.name}>'
