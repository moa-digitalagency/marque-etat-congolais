# models/__init__.py
from flask_sqlalchemy import SQLAlchemy
from models.user import User
from models.template import Template
from models.logo import LogoGeneration
from models.shared_link import SharedLink

db = SQLAlchemy()

__all__ = ['db', 'User', 'Template', 'LogoGeneration', 'SharedLink']
