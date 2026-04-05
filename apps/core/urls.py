from django.urls import path
from .views_setup import setup_superuser, setup_status

urlpatterns = [
    path('setup/status/', setup_status, name='setup-status'),
    path('setup/superuser/', setup_superuser, name='setup-superuser'),
]
