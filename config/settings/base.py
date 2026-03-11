"""
ImoOS — Base Django Settings
Shared by all environments (development, staging, production).
"""
from pathlib import Path
from decouple import config, Csv
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# =============================================================
# Security
# =============================================================
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='', cast=Csv())

# =============================================================
# Multi-Tenant (django-tenants)
# =============================================================
SHARED_APPS = [
    'django_tenants',
    'apps.tenants',      # Must be first in SHARED_APPS

    # Django core (public schema only)
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.gis',

    # Shared infrastructure
    'apps.users',
    'apps.core',

    # Third party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'simple_history',
]

TENANT_APPS = [
    'django.contrib.contenttypes',

    # Business modules (each gets its own schema)
    'apps.projects',
    'apps.inventory',
    'apps.crm',
    'apps.sales',
    'apps.contracts',
    'apps.payments',
    'apps.construction',
    'apps.marketplace',
]

INSTALLED_APPS = list(SHARED_APPS) + [app for app in TENANT_APPS if app not in SHARED_APPS]

TENANT_MODEL = 'tenants.Client'
TENANT_DOMAIN_MODEL = 'tenants.Domain'
PUBLIC_SCHEMA_URLCONF = config('PUBLIC_SCHEMA_URLCONF', default='config.urls_public')
SHOW_PUBLIC_IF_NO_TENANT_FOUND = False

# =============================================================
# Database (PostgreSQL + PostGIS)
# =============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME', default='imos'),
        'USER': config('DB_USER', default='imos'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
    }
}
DATABASE_ROUTERS = ['django_tenants.routers.TenantSyncRouter']

# =============================================================
# Middleware
# =============================================================
MIDDLEWARE = [
    'apps.tenants.middleware.ImoOSTenantMiddleware',  # MUST be first
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'simple_history.middleware.HistoryRequestMiddleware',
]

ROOT_URLCONF = 'config.urls'

# =============================================================
# Authentication
# =============================================================
AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'guardian.backends.ObjectPermissionBackend',
]

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=config('JWT_ACCESS_TOKEN_LIFETIME_MINUTES', default=15, cast=int)),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=config('JWT_REFRESH_TOKEN_LIFETIME_DAYS', default=7, cast=int)),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    # Custom claim added in token serializer
    # 'tenant_schema': set by CustomTokenObtainPairSerializer
}

# =============================================================
# REST Framework
# =============================================================
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
    ],
    'DEFAULT_PAGINATION_CLASS': 'apps.core.pagination.StandardResultsPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': [
        'apps.core.throttling.TenantScopedThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour',
        'tenant': '5000/hour',
    },
}

# =============================================================
# Cache (Redis)
# =============================================================
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': config('REDIS_URL', default='redis://localhost:6379/0'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# =============================================================
# Celery
# =============================================================
CELERY_BROKER_URL = config('CELERY_BROKER_URL', default='redis://localhost:6379/1')
CELERY_RESULT_BACKEND = config('CELERY_RESULT_BACKEND', default='redis://localhost:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 270
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TIMEZONE = 'Atlantic/Cape_Verde'

# =============================================================
# Storage (S3-compatible)
# =============================================================
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = config('AWS_ACCESS_KEY_ID', default='')
AWS_SECRET_ACCESS_KEY = config('AWS_SECRET_ACCESS_KEY', default='')
AWS_STORAGE_BUCKET_NAME = config('AWS_STORAGE_BUCKET_NAME', default='imos-media')
AWS_S3_ENDPOINT_URL = config('AWS_S3_ENDPOINT_URL', default=None)
AWS_S3_CUSTOM_DOMAIN = config('AWS_S3_CUSTOM_DOMAIN', default=None)
AWS_DEFAULT_ACL = 'private'
AWS_S3_FILE_OVERWRITE = False
MEDIA_URL = config('MEDIA_URL', default='/media/')

# =============================================================
# Internationalization
# =============================================================
LANGUAGE_CODE = 'pt-pt'
TIME_ZONE = 'Atlantic/Cape_Verde'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('pt-pt', 'Português (Cabo Verde)'),
    ('pt-ao', 'Português (Angola)'),
    ('fr-sn', 'Français (Sénégal)'),
]

# =============================================================
# Audit History
# =============================================================
SIMPLE_HISTORY_HISTORY_CHANGE_REASON_USE_TEXT_FIELD = True
SIMPLE_HISTORY_REVERT_DISABLED = False

# =============================================================
# API Documentation (drf-spectacular)
# =============================================================
SPECTACULAR_SETTINGS = {
    'TITLE': 'ImoOS API',
    'DESCRIPTION': 'Sistema Operativo para Promotoras Imobiliárias — Cabo Verde',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
}

# =============================================================
# Tenant Domain
# =============================================================
TENANT_BASE_DOMAIN = config('TENANT_BASE_DOMAIN', default='imos.cv')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
