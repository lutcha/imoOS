"""
Setup views for initial configuration.
These endpoints are only available when DEBUG=True or when no superusers exist.
"""
import os
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
    This endpoint is protected by a secret token.
    """
    # Check if setup is allowed
    secret_token = os.environ.get('SETUP_SECRET_TOKEN', 'imos-setup-2026')
    provided_token = request.headers.get('X-Setup-Token')
    
    if provided_token != secret_token:
        return Response(
            {'error': 'Invalid setup token'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Check if superusers already exist
    connection.set_schema_to_public()
    if User.objects.filter(is_superuser=True).exists():
        return Response(
            {'error': 'Superuser already exists'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create superuser
    email = request.data.get('email', 'admin@proptech.cv')
    password = request.data.get('password', 'ImoOS2026')
    first_name = request.data.get('first_name', 'Admin')
    last_name = request.data.get('last_name', 'ImoOS')
    
    user = User.objects.create_superuser(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    
    return Response({
        'message': 'Superuser created successfully',
        'email': email,
        'password': password
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([AllowAny])
def setup_status(request):
    """Check if setup is needed (no superusers exist)."""
    connection.set_schema_to_public()
    needs_setup = not User.objects.filter(is_superuser=True).exists()
    
    return Response({
        'needs_setup': needs_setup,
        'has_superuser': not needs_setup
    })
