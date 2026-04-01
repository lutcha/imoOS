"""
ImoOS — Staging Settings
Mirrors production closely; used for pre-release validation on DigitalOcean App Platform.
"""
from .base import *  # noqa
from decouple import config, Csv

# =============================================================
# Core
# =============================================================
DEBUG = False
SECRET_KEY = config('SECRET_KEY')
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='.ondigitalocean.app,staging.imos.cv', cast=Csv())

# =============================================================
# Database
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
# Security Headers
# =============================================================
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # DO App Platform terminates SSL at the load balancer
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 3600          # 1h — lower than prod while validating
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = False         # Don't preload on staging
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'

# =============================================================
# CORS — staging frontend only
# =============================================================
CORS_ALLOWED_ORIGINS = config('CORS_ALLOWED_ORIGINS', cast=Csv(), default='')
CORS_ALLOW_CREDENTIALS = True

# =============================================================
# Static & Media
# =============================================================
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Media via DigitalOcean Spaces (same bucket, staging/ prefix)
AWS_LOCATION = 'staging'

# =============================================================
# Email — SMTP se configurado, senão console (staging sem email config arranca na mesma)
# =============================================================
_email_host = config('EMAIL_HOST', default='')
if _email_host:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = _email_host
    EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
    EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
    EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
    EMAIL_USE_TLS = True
else:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='ImoOS Staging <noreply@staging.imos.cv>')

# =============================================================
# PII Scrubbing — called by Sentry before_send
# =============================================================
def _scrub_sensitive_data(event, hint):
    """Remove PII from Sentry events before transmission. LGPD Art. 11."""
    # Strip request headers that may contain auth tokens
    if 'request' in event:
        headers = event['request'].get('headers', {})
        for key in ('Authorization', 'Cookie', 'X-Api-Key'):
            headers.pop(key, None)
            headers.pop(key.lower(), None)

        # Remove query string (may contain tokens)
        event['request'].pop('query_string', None)

    # Strip user context entirely
    event.pop('user', None)

    return event


# =============================================================
# Sentry — LGPD compliant
# =============================================================
SENTRY_DSN = config('SENTRY_DSN', default='')

if SENTRY_DSN and SENTRY_DSN.startswith('https://') and '@sentry.io' in SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
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
        environment='staging',
        release=config('APP_VERSION', default='unknown'),

        # ---------- LGPD Compliance ----------
        # Art. 11, Lei 133/V/2019 — minimização de dados pessoais
        send_default_pii=False,      # NEVER send PII (emails, IPs, user IDs)
        request_bodies='small',      # Only capture small request bodies
        # -----------------------------------

        traces_sample_rate=0.2,      # 20% of transactions for performance
        profiles_sample_rate=0.1,
        before_send=_scrub_sensitive_data,
    )

# =============================================================
# Logging
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
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
        'apps': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
