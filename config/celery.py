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
