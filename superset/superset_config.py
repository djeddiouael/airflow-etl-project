# Superset Configuration
import os

# Secret key pour la sécurité
SECRET_KEY = os.environ.get('SUPERSET_SECRET_KEY', 'supersecretkey123456789')

# Configuration de la base de données metadata Superset
# Use PostgreSQL for Superset metadata
SUPERSET_DB_USER = os.environ.get('SUPERSET_DB_USER', 'airflow')
SUPERSET_DB_PASSWORD = os.environ.get('SUPERSET_DB_PASSWORD', 'airflow')
SUPERSET_DB_HOST = os.environ.get('SUPERSET_DB_HOST', 'postgres')
SUPERSET_DB_PORT = os.environ.get('SUPERSET_DB_PORT', '5432')
SUPERSET_DB_NAME = os.environ.get('SUPERSET_DB_NAME', 'superset_db')

SQLALCHEMY_DATABASE_URI = f'postgresql+psycopg2://{SUPERSET_DB_USER}:{SUPERSET_DB_PASSWORD}@{SUPERSET_DB_HOST}:{SUPERSET_DB_PORT}/{SUPERSET_DB_NAME}'

# Activer les fonctionnalités
FEATURE_FLAGS = {
    'ENABLE_TEMPLATE_PROCESSING': True,
    'DASHBOARD_NATIVE_FILTERS': True,
    'DASHBOARD_CROSS_FILTERS': True,
}

# Configuration du cache
CACHE_CONFIG = {
    'CACHE_TYPE': 'SimpleCache',
    'CACHE_DEFAULT_TIMEOUT': 300,
}

# Langues supportées
LANGUAGES = {
    'en': {'flag': 'us', 'name': 'English'},
    'fr': {'flag': 'fr', 'name': 'French'},
}

# Configuration de sécurité
WTF_CSRF_ENABLED = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'

