from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

# Disable S3 in local dev — use filesystem
DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'
MEDIA_ROOT = BASE_DIR / 'media'
MEDIA_URL = '/media/'

# Show SQL queries in debug
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE = ['debug_toolbar.middleware.DebugToolbarMiddleware'] + MIDDLEWARE
INTERNAL_IPS = ['127.0.0.1']

# Looser CORS for local dev
CORS_ALLOW_ALL_ORIGINS = True

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# ⚠️ TEMPORÁRIO: Bypass de autenticação para desenvolvimento
# ⚠️ REMOVER antes de commitar para produção!
# ⚠️ Permite login sem validar credenciais (apenas para testes locais)
DEV_SKIP_AUTH = True
