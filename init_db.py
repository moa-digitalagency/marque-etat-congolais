#!/usr/bin/env python
"""
Database initialization script.
Creates all tables, indexes, and seeds default templates.

Usage:
    python init_db.py
"""

import os
import sys
from datetime import datetime

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from models import User, Template, LogoGeneration, SharedLink
from config.constants import INSTITUTION_TYPES

def init_database():
    """Initialize database: create tables, add seed data"""
    app = create_app()

    with app.app_context():
        print("🔧 Creating all tables...")
        db.create_all()
        print("✅ Tables created successfully")

        # Check if templates already exist
        existing_templates = Template.query.count()
        if existing_templates > 0:
            print(f"⚠️  Templates already exist ({existing_templates}). Skipping seed...")
            return

        print("\n🌱 Seeding default templates...")

        # Define default templates
        templates_data = [
            {
                'name': 'Ambassade RDC',
                'description': 'Modèle pour ambassades de la RDC à l\'étranger',
                'institution_type': 'Ambassade',
                'params': {
                    'armoiries_height': 624,
                    'spacing': 85,
                    'text_spacing': 80,
                    'font_size': 105,
                    'line_spacing': 110,
                    'text_color': [0, 0, 0, 255]
                }
            },
            {
                'name': 'Ministère Standard',
                'description': 'Modèle standard pour ministères',
                'institution_type': 'Ministère',
                'params': {
                    'armoiries_height': 624,
                    'spacing': 85,
                    'text_spacing': 80,
                    'font_size': 100,
                    'line_spacing': 110,
                    'text_color': [0, 0, 0, 255]
                }
            },
            {
                'name': 'Institution Autonome',
                'description': 'Modèle pour institutions autonomes',
                'institution_type': 'Institution Autonome',
                'params': {
                    'armoiries_height': 600,
                    'spacing': 80,
                    'text_spacing': 75,
                    'font_size': 95,
                    'line_spacing': 105,
                    'text_color': [0, 0, 0, 255]
                }
            },
            {
                'name': 'Établissement Public',
                'description': 'Modèle pour établissements publics',
                'institution_type': 'Établissement Public',
                'params': {
                    'armoiries_height': 624,
                    'spacing': 85,
                    'text_spacing': 80,
                    'font_size': 100,
                    'line_spacing': 110,
                    'text_color': [0, 0, 0, 255]
                }
            }
        ]

        for template_data in templates_data:
            template = Template(
                name=template_data['name'],
                description=template_data['description'],
                institution_type=template_data['institution_type'],
                params=template_data['params'],
                created_by_admin=None,  # Seed templates have no creator
                is_active=True
            )
            db.session.add(template)
            print(f"  ✓ Added template: {template.name}")

        db.session.commit()
        print("✅ Templates seeded successfully\n")

        # Print summary
        user_count = User.query.count()
        template_count = Template.query.count()

        print("📊 Database Summary:")
        print(f"  Users: {user_count}")
        print(f"  Templates: {template_count}")
        print("\n🚀 Database initialized successfully!")
        print("\nNext steps:")
        print("  1. Create admin user: python create_admin.py")
        print("  2. Run Flask app: python app.py")

if __name__ == '__main__':
    init_database()
