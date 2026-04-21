"""
ImoOS — Production Settings
Hardened for imos.cv on DigitalOcean App Platform.
Mirrors staging.py but with full HSTS, stricter CSP, and no debug tooling.
"""
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.redis import RedisIntegration

from .base import *  # noqa
from decouple import config, Csv

# =============================================================
# Core
# =============================================================
DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# =============================================================
# Database — DO Managed PostgreSQL
# =============================================================
DATABASES = {
    'default': {
        'ENGINE': 'django_tenants.postgresql_backend',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 60,
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# =============================================================
# Security Headers (production-grade)
# =============================================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000         # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True             # Submit to HSTS preload list
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================
# CORS — production & staging frontend
# =============================================================
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='https://demo.proptech.cv,https://proptech.cv')
CORS_ALLOW_CREDENTIALS = True

# Ensure x-tenant-schema and all others are allowed for multi-tenancy
from corsheaders.defaults import default_headers
CORS_ALLOW_HEADERS = list(default_headers) + [
    'x-tenant-schema',
]
CORS_EXPOSE_HEADERS = ['Content-Disposition', 'x-tenant-schema']

# CSRF Trusted Origins for tenant subdomains
CSRF_TRUSTED_ORIGINS = [
    'https://demo.proptech.cv',
    'https://proptech.cv',
]


# =============================================================
# Static & Media
# =============================================================
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'


# Media via DigitalOcean Spaces (production/ prefix)
AWS_LOCATION = 'production'

# =============================================================
# Email — SMTP in production
# =============================================================
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='ImoOS <noreply@imos.cv>')

# =============================================================
# Celery / Cache — inherit from base.py via env vars
# CELERY_BROKER_URL, REDIS_URL must be set as env vars
# =============================================================

# =============================================================
# PII Scrubbing — called by Sentry before_send
# =============================================================
def _scrub_sensitive_data(event, hint):
    """Remove PII from Sentry events before transmission. LGPD Art. 11."""
    if 'request' in event:
        headers = event['request'].get('headers', {})
        for key in ('Authorization', 'Cookie', 'X-Api-Key'):
            headers.pop(key, None)
            headers.pop(key.lower(), None)
        event['request'].pop('query_string', None)
    event.pop('user', None)
    return event


# =============================================================
# Sentry — LGPD compliant
# =============================================================
SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
                signals_spans=False,
            ),
            CeleryIntegration(monitor_beat_tasks=True),
            RedisIntegration(),
        ],
        environment='production',
        release=config('APP_VERSION', default='unknown'),

        # ---------- LGPD Compliance ----------
        send_default_pii=False,
        request_bodies='small',
        # -----------------------------------

        traces_sample_rate=0.05,     # 5% — lower than staging
        profiles_sample_rate=0.02,
        before_send=_scrub_sensitive_data,
    )

# =============================================================
# Logging — structured JSON to stdout (DO App Platform collects it)
# =============================================================
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'pythonjsonlogger.jsonlogger.JsonFormatter',
            'format': '%(asctime)s %(levelname)s %(name)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'json',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'WARNING',          # Quieter than staging in production
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}
