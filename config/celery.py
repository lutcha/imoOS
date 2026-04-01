import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

app = Celery('imos')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# Store task results in DB for monitoring (Sprint 7)
app.conf.update(
    result_extended=True,  # Store task name, args, kwargs
    result_backend='django-db',  # Use django_celery_results
)

# Fix for DO Redis SSL (rediss:// requires ssl_cert_reqs)
if app.conf.broker_url and app.conf.broker_url.startswith('rediss://') and 'ssl_cert_reqs' not in app.conf.broker_url:
    sep = '&' if '?' in app.conf.broker_url else '?'
    app.conf.broker_url = f"{app.conf.broker_url}{sep}ssl_cert_reqs=CERT_NONE"

if app.conf.result_backend and app.conf.result_backend.startswith('rediss://') and 'ssl_cert_reqs' not in app.conf.result_backend:
    sep = '&' if '?' in app.conf.result_backend else '?'
    app.conf.result_backend = f"{app.conf.result_backend}{sep}ssl_cert_reqs=CERT_NONE"
