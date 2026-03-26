# services/template_service.py
"""Template management service"""

from models import db, Template

class TemplateService:
    """Service for template CRUD operations"""

    @staticmethod
    def get_active_templates():
        """Get all active templates"""
        return Template.query.filter_by(is_active=True).all()

    @staticmethod
    def get_template_by_id(template_id: int) -> Template:
        """Get template by ID"""
        return Template.query.get(template_id)

    @staticmethod
    def create_template(
        name: str,
        description: str = None,
        institution_type: str = None,
        params: dict = None,
        created_by_admin: int = None
    ) -> Template:
        """
        Create new template.

        Args:
            name: Template name
            description: Template description
            institution_type: Type of institution
            params: Generation parameters (dict)
            created_by_admin: ID of admin who created template

        Returns:
            Created Template object
        """
        template = Template(
            name=name,
            description=description,
            institution_type=institution_type,
            params=params or {},
            created_by_admin=created_by_admin,
            is_active=True
        )

        db.session.add(template)
        db.session.commit()

        return template

    @staticmethod
    def update_template(template_id: int, **kwargs) -> Template:
        """Update template fields"""
        template = Template.query.get(template_id)

        if not template:
            raise ValueError(f"Template {template_id} not found")

        for key, value in kwargs.items():
            if hasattr(template, key):
                setattr(template, key, value)

        db.session.commit()

        return template

    @staticmethod
    def delete_template(template_id: int) -> bool:
        """Soft delete template (set is_active=False)"""
        template = Template.query.get(template_id)

        if not template:
            raise ValueError(f"Template {template_id} not found")

        template.is_active = False
        db.session.commit()

        return True
