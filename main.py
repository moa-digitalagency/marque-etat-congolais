#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Logo Generator WebApp - Main Entry Point
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Ensure FLASK_APP is set
os.environ.setdefault('FLASK_APP', 'app.py')
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app, db
from models import User, Template, LogoGeneration, SharedLink

# Create Flask app
app = create_app()

# Shell context for flask shell
@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Template': Template,
        'LogoGeneration': LogoGeneration,
        'SharedLink': SharedLink
    }

if __name__ == '__main__':
    # Initialize database if needed (check if tables exist)
    with app.app_context():
        # Import after app context
        from init_db import init_database
        from sqlalchemy import text

        # Initialize database on first run
        try:
            # Try to query User table to check if DB is initialized
            db.session.execute(text("SELECT COUNT(*) FROM \"user\""))
        except:
            # If error, initialize database
            print("📊 Initializing database...")
            init_database()
            print("✅ Database initialized!")

    # Run the app
    print("🚀 Starting Logo Generator WebApp...")
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)
