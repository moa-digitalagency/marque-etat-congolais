# config/constants.py

# Logo generation defaults
ARMOIRIES_HEIGHT = 624
SPACING = 85
TEXT_SPACING = 80
FONT_SIZE = 105
LINE_SPACING = 110
TEXT_COLOR = (0, 0, 0, 255)

# Text splitting
MAX_LINES = 5
MAX_WORDS_PER_LINE = 3

# File paths
LOGO_ASSETS_PATH = 'logo_assets'
ARMOIRIES_FILE = 'armoiries.png'
LIGNE_ETAT_FILE = 'ligne_etat.png'
FONT_FILE = '../font/cooper-hewitt/CooperHewitt-Bold.otf'

# Supported languages
SUPPORTED_LANGUAGES = ['fr', 'lingala', 'swahili']

# Share link settings
SHARE_TOKEN_LENGTH = 32
SHARE_LINK_EXPIRES_DAYS = None  # None = never expires

# Institution types
INSTITUTION_TYPES = [
    'Ambassade',
    'Ministère',
    'Direction Générale',
    'Institution Autonome',
    'Établissement Public',
    'Autre'
]
