# services/share_service.py
"""Shared link management service"""

from models import db, SharedLink, LogoGeneration
from datetime import datetime, timedelta
from config.constants import SHARE_LINK_EXPIRES_DAYS

class ShareService:
    """Service for managing public share links"""

    @staticmethod
    def create_share_link(logo_id: int, created_by: int = None, expires_days: int = None) -> SharedLink:
        """
        Create public share link for a logo.

        Args:
            logo_id: ID of logo to share
            created_by: ID of user creating share link
            expires_days: Days until link expires (None = never)

        Returns:
            SharedLink object
        """
        logo = LogoGeneration.query.get(logo_id)

        if not logo:
            raise ValueError(f"Logo {logo_id} not found")

        # Check if link already exists
        existing = SharedLink.query.filter_by(logo_id=logo_id).first()
        if existing:
            return existing

        # Calculate expiry
        expires_at = None
        if expires_days is not None:
            expires_at = datetime.utcnow() + timedelta(days=expires_days)
        elif SHARE_LINK_EXPIRES_DAYS is not None:
            expires_at = datetime.utcnow() + timedelta(days=SHARE_LINK_EXPIRES_DAYS)

        share_link = SharedLink(
            logo_id=logo_id,
            token_public=SharedLink.generate_token(),
            created_by=created_by,
            expires_at=expires_at
        )

        db.session.add(share_link)
        db.session.commit()

        return share_link

    @staticmethod
    def get_share_link_by_token(token: str) -> SharedLink:
        """Get share link by token"""
        return SharedLink.query.filter_by(token_public=token).first()

    @staticmethod
    def is_share_link_valid(share_link: SharedLink) -> bool:
        """Check if share link is valid and not expired"""
        if not share_link:
            return False

        return not share_link.is_expired()

    @staticmethod
    def record_share_view(share_link: SharedLink):
        """Record that share link was viewed"""
        share_link.increment_view_count()
        db.session.commit()
