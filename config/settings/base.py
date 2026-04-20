import os
import ssl
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
# Security Hardening (Sprint 7 - Prompt 05)
# =============================================================

# Security headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
REFERRER_POLICY = 'strict-origin-when-cross-origin'

# CSRF Security
CSRF_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_TRUSTED_ORIGINS = config('CSRF_TRUSTED_ORIGINS', default='', cast=Csv())

# Session Security
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_AGE = 1209600  # 2 weeks
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# SSL/HTTPS (production only)
if not DEBUG:
    SECURE_SSL_REDIRECT = config('SECURE_SSL_REDIRECT', default=True, cast=bool)
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Content Security Policy (CSP) - Updated for django-csp 4.0
CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "'unsafe-inline'", "'unsafe-eval'", 'https://*.sentry.io'),
        'style-src': ("'self'", "'unsafe-inline'", 'https://fonts.googleapis.com'),
        'font-src': ("'self'", 'https://fonts.gstatic.com', 'data:'),
        'img-src': ("'self'", 'data:', 'blob:', 'https:'),
        'connect-src': ("'self'", 'https://*.sentry.io', 'https://*.imos.cv', 'https://*.proptech.cv', 'https://proptech.cv'),
        'frame-src': ("'self'",),
        'object-src': ("'none'",),
        'base-uri': ("'self'",),
        'form-action': ("'self'",),
    }
}

# Permissions Policy (formerly Feature Policy)
PERMISSIONS_POLICY = {
    'accelerometer': [],
    'ambient-light-sensor': [],
    'autoplay': [],
    'camera': [],
    'display-capture': [],
    'document-domain': [],
    'encrypted-media': [],
    'fullscreen': [],
    'geolocation': [],
    'gyroscope': [],
    'magnetometer': [],
    'microphone': [],
    'midi': [],
    'payment': [],
    'picture-in-picture': [],
    'usb': [],
}

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
    # 'django.contrib.gis',

    # Shared infrastructure
    'apps.users',
    'apps.core',

    # Observability (Sprint 7)
    'django_prometheus',

    # Third party
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'simple_history',
    'django_celery_results',  # Required for task monitoring
    'django_celery_beat',     # Required for scheduled tasks (Sprint 7)
    
    # Security (Sprint 7 - Prompt 05)
    'csp',
    'django_permissions_policy',
]

TENANT_APPS = [
    'django.contrib.contenttypes',

    # Per-tenant user roles (replaces global User.role for auth decisions)
    'apps.memberships',

    # Business modules (each gets its own schema)
    'apps.projects',
    'apps.inventory',
    'apps.crm',
    'apps.sales',
    'apps.contracts',
    'apps.payments',
    'apps.construction',
    'apps.marketplace',
    'apps.investors',
    'apps.integrations',  # WhatsApp Business API integration
    'apps.budget',  # Orçamentos e base de preços CV
    'apps.workflows',  # Integração e automação de workflows
]

# =============================================================
# CORS & Security (Sprint 5 Staging Fix)
# =============================================================
from corsheaders.defaults import default_headers

CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-tenant-schema',
]

# Default allowed origins for proptech.cv demo
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='https://demo.proptech.cv,https://proptech.cv')
CORS_ALLOW_CREDENTIALS = True

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
    'django_prometheus.middleware.PrometheusBeforeMiddleware',  # Sprint 7 - must be first
    'apps.tenants.middleware.ImoOSTenantMiddleware',  # MUST be after Prometheus
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
    'django_prometheus.middleware.PrometheusAfterMiddleware',  # Sprint 7 - must be last
]

ROOT_URLCONF = 'config.urls'

# =============================================================
# Templates
# =============================================================
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

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
import re as _re


def _strip_ssl_cert_reqs(url: str) -> str:
    """Remove ssl_cert_reqs from URL — DO App Platform injects it but
    redis-py 4+ rejects the string form. SSL is handled via CONNECTION_POOL_KWARGS."""
    url = _re.sub(r'[?&]ssl_cert_reqs=[^&]*', '', url)
    # Fix leftover ?& or trailing ?
    url = _re.sub(r'\?&', '?', url).rstrip('?&')
    return url


_redis_url = _strip_ssl_cert_reqs(config('REDIS_URL', default='redis://localhost:6379/0'))
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': _redis_url,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            # DO Managed Redis/Valkey uses TLS (rediss://) with internal CA —
            # disable cert verification for managed clusters
            'CONNECTION_POOL_KWARGS': {
                'ssl_cert_reqs': None,
            } if _redis_url.startswith('rediss://') else {},
        }
    }
}

# =============================================================
# Celery
# =============================================================
# DO Managed Redis/Valkey TLS — ensure rediss:// URLs have ssl_cert_reqs
def _fix_rediss_url(url):
    if url and url.startswith('rediss://') and 'ssl_cert_reqs' not in url:
        sep = '&' if '?' in url else '?'
        return f"{url}{sep}ssl_cert_reqs=CERT_NONE"
    return url

CELERY_BROKER_URL = _fix_rediss_url(config('CELERY_BROKER_URL', default='redis://localhost:6379/1'))
CELERY_RESULT_BACKEND = _fix_rediss_url(config('CELERY_RESULT_BACKEND', default='django-db'))

# Robust SSL fix for Celery 5.3+ on DigitalOcean
if CELERY_BROKER_URL and CELERY_BROKER_URL.startswith('rediss://'):
    CELERY_BROKER_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE
    }

if CELERY_RESULT_BACKEND and CELERY_RESULT_BACKEND.startswith('rediss://'):
    CELERY_REDIS_BACKEND_USE_SSL = {
        'ssl_cert_reqs': ssl.CERT_NONE
    }
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 300
CELERY_TASK_SOFT_TIME_LIMIT = 270
CELERY_WORKER_PREFETCH_MULTIPLIER = 1
CELERY_TIMEZONE = 'Atlantic/Cape_Verde'

# Celery Beat — Scheduled tasks (Sprint 7)
CELERY_BEAT_SCHEDULE = {
    # Monitor failed tasks every hour
    'monitor-failed-tasks-hourly': {
        'task': 'apps.core.tasks.monitor_failed_tasks',
        'schedule': 3600.0,  # seconds (1 hour)
    },
    # Cleanup old task results daily
    'cleanup-task-results-daily': {
        'task': 'apps.core.tasks.cleanup_old_task_results',
        'schedule': 86400.0,  # seconds (1 day)
    },
}

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
DJANGO_SUPERADMIN_URL = config('DJANGO_SUPERADMIN_URL', default='django-admin/')

# =============================================================
# SaaS Plan Limits
# =============================================================
PLAN_LIMITS = {
    'starter':    {'max_projects': 3,   'max_units': 100,  'max_users': 5},
    'pro':        {'max_projects': 15,  'max_units': 1000, 'max_users': 50},
    'enterprise': {'max_projects': 999, 'max_units': 9999, 'max_users': 999},
}

# =============================================================
# imo.cv Marketplace Integration
# =============================================================
IMOCV_API_BASE_URL = config('IMOCV_API_BASE_URL', default='https://api.imo.cv/v1')
IMOCV_WEBHOOK_SECRET = config('IMOCV_WEBHOOK_SECRET', default='')

# =============================================================
# Sentry Error Tracking (Sprint 7)
# =============================================================
SENTRY_DSN = config('SENTRY_DSN', default='')
SENTRY_ENVIRONMENT = config('SENTRY_ENVIRONMENT', default='development')

if SENTRY_DSN and SENTRY_DSN.startswith('https://') and '@sentry.io' in SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    
    def _scrub_tenant_pii(event, hint):
        """
        Remove PII from Sentry events (LGPD compliance).
        Filters Authorization headers and cookies from request data.
        """
        if 'request' in event:
            headers = event['request'].get('headers', {})
            for key in list(headers.keys()):
                if key.lower() in ('authorization', 'cookie'):
                    headers[key] = '[Filtered]'
        return event
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration(), RedisIntegration()],
        traces_sample_rate=0.1,        # 10% of requests in production
        profiles_sample_rate=0.05,     # 5% for profiling
        environment=SENTRY_ENVIRONMENT,
        send_default_pii=False,        # LGPD: no PII in reports
        before_send=_scrub_tenant_pii, # Remove sensitive data
    )

# =============================================================
# Structured Logging (Sprint 7)
# =============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(name)s %(levelname)s %(message)s %(tenant_schema)s',
        },
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'filters': {
        'require_debug_false': {'()': 'django.utils.log.RequireDebugFalse'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
        'sentry': {
            'level': 'ERROR',
            'class': 'sentry_sdk.integrations.logging.EventHandler',
            'filters': ['require_debug_false'],
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'apps': {'handlers': ['console', 'sentry'], 'level': 'INFO', 'propagate': False},
        'celery': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
