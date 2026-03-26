# services/i18n_service.py
"""Internationalization (i18n) service"""

import json
import os
from config.constants import SUPPORTED_LANGUAGES

class I18nService:
    """Service for managing translations"""

    _translations = {}

    @classmethod
    def load_translations(cls):
        """Load all translation files"""
        lang_dir = 'lang'

        for lang in SUPPORTED_LANGUAGES:
            lang_file = os.path.join(lang_dir, f'{lang}.json')

            if os.path.exists(lang_file):
                with open(lang_file, 'r', encoding='utf-8') as f:
                    cls._translations[lang] = json.load(f)
            else:
                cls._translations[lang] = {}

    @classmethod
    def get_text(cls, key: str, language: str = 'fr', default: str = None) -> str:
        """
        Get translated text by key.

        Args:
            key: Translation key (e.g., 'common.welcome')
            language: Language code
            default: Default text if key not found

        Returns:
            Translated text or default value
        """
        if not cls._translations:
            cls.load_translations()

        if language not in cls._translations:
            return default or key

        # Navigate nested keys (e.g., 'common.welcome' → translations['common']['welcome'])
        keys = key.split('.')
        value = cls._translations[language]

        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default or key

    # Jinja2 template filter
    @staticmethod
    def jinja_filter(key: str, language: str = 'fr') -> str:
        """Jinja2 filter for translations in templates"""
        return I18nService.get_text(key, language)
