"""
Setup views for initial platform configuration.
ONLY available when DEBUG=True (development/staging) AND no superusers exist.
NOT exposed in production (settings.DEBUG = False).
"""
import os
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db import connection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

User = get_user_model()


@api_view(['POST'])
@permission_classes([AllowAny])
def setup_superuser(request):
    """
    Create initial superuser if none exists.
    Protected by SETUP_SECRET_TOKEN env var (required — no insecure default).
    Only works when DEBUG=True.
    """
    if not settings.DEBUG:
        return Response({'error': 'Not available'}, status=status.HTTP_404_NOT_FOUND)

    secret_token = os.environ.get('SETUP_SECRET_TOKEN')
    if not secret_token:
        return Response(
            {'error': 'SETUP_SECRET_TOKEN environment variable not set'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    provided_token = request.headers.get('X-Setup-Token')
    if not provided_token or provided_token != secret_token:
        return Response({'error': 'Invalid setup token'}, status=status.HTTP_403_FORBIDDEN)

    connection.set_schema_to_public()

    if User.objects.filter(is_superuser=True).exists():
        return Response({'message': 'Superuser already exists'}, status=status.HTTP_200_OK)

    email = request.data.get('email', 'admin@proptech.cv')
    password = request.data.get('password')
    if not password:
        return Response({'error': 'password is required'}, status=status.HTTP_400_BAD_REQUEST)

    User.objects.create_superuser(
        email=email,
        password=password,
        first_name=request.data.get('first_name', 'Admin'),
        last_name=request.data.get('last_name', 'ImoOS'),
    )

    # Never return the password
    return Response({'message': 'Superuser created', 'email': email}, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def setup_status(request):
    """Check if setup is needed. Only works when DEBUG=True."""
    if not settings.DEBUG:
        return Response({'error': 'Not available'}, status=status.HTTP_404_NOT_FOUND)

    connection.set_schema_to_public()
    has_superuser = User.objects.filter(is_superuser=True).exists()
    return Response({'needs_setup': not has_superuser, 'has_superuser': has_superuser})
