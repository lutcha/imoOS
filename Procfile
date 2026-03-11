web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120 --log-file -
worker: celery -A config.celery worker --loglevel=info --concurrency=2
beat: celery -A config.celery beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
release: python manage.py migrate_schemas --shared && python manage.py migrate_schemas && python manage.py collectstatic --noinput
