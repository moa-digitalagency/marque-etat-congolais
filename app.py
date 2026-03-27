"""
Flask application factory.
Initializes and configures the Flask app with all extensions and blueprints.
"""

from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from models import db, User
from config.settings import get_config
from services import I18nService

def create_app(config=None):
    """
    Application factory function.

    Args:
        config: Configuration object (defaults to environment-based config)

    Returns:
        Configured Flask app instance
    """
    app = Flask(__name__)

    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)

    # Initialize extensions
    db.init_app(app)
    csrf = CSRFProtect(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Veuillez vous connecter pour accéder à cette page.'

    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for Flask-Login"""
        return User.query.get(int(user_id))

    # Load translations
    I18nService.load_translations()

    # Register blueprints
    from routes.auth import auth_bp
    from routes.public import public_bp
    from routes.dashboard import dashboard_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(public_bp, url_prefix='')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    # Root route redirect
    @app.route('/')
    def root():
        """Redirect root to login or dashboard"""
        from flask_login import current_user
        if current_user.is_authenticated:
            return __import__('flask').redirect(__import__('flask').url_for('dashboard.index'))
        return __import__('flask').redirect(__import__('flask').url_for('auth.login'))

    # Template filters
    @app.template_filter('t')
    def translate_filter(key, language=None):
        """Jinja2 filter for translations"""
        if language is None:
            # Get language from current user if available
            from flask_login import current_user
            language = current_user.language if current_user.is_authenticated else 'fr'
        return I18nService.get_text(key, language)

    # Context processor for template variables
    @app.context_processor
    def inject_user():
        """Inject current_user into template context"""
        from flask_login import current_user
        return dict(current_user=current_user)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Page not found'}, 404

    @app.errorhandler(500)
    def server_error(error):
        return {'error': 'Server error'}, 500

    return app


if __name__ == '__main__':
    # Create and run app for development
    app = create_app()

    with app.app_context():
        # Create tables if they don't exist
        db.create_all()

    # Run development server
    app.run(debug=True, host='0.0.0.0', port=5000)
