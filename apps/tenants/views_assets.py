"""
Tenant Assets API — Logo & Favicon upload to S3/Spaces
"""
import uuid
import boto3
from botocore.exceptions import ClientError
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from apps.users.permissions import IsTenantAdmin
from .models import TenantSettings


def get_s3_client():
    """Get S3 client configured for DigitalOcean Spaces."""
    return boto3.client(
        's3',
        endpoint_url=settings.AWS_S3_ENDPOINT_URL,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name='ams3'  # DigitalOcean Amsterdam region
    )


def upload_to_spaces(file_obj, tenant_slug, asset_type):
    """
    Upload file to DigitalOcean Spaces.
    
    Args:
        file_obj: Django UploadedFile
        tenant_slug: Tenant slug for path organization
        asset_type: 'logo' or 'favicon'
    
    Returns:
        dict with url and s3_key
    """
    s3 = get_s3_client()
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    
    # Generate unique filename
    ext = file_obj.name.split('.')[-1].lower()
    filename = f"{asset_type}-{uuid.uuid4().hex[:8]}.{ext}"
    s3_key = f"tenants/{tenant_slug}/assets/{filename}"
    
    try:
        s3.upload_fileobj(
            file_obj,
            bucket,
            s3_key,
            ExtraArgs={
                'ACL': 'public-read',
                'ContentType': file_obj.content_type,
            }
        )
        
        # Construct public URL
        url = f"{settings.AWS_S3_ENDPOINT_URL}/{bucket}/{s3_key}"
        
        return {
            'success': True,
            'url': url,
            's3_key': s3_key,
            'filename': filename,
        }
    except ClientError as e:
        return {
            'success': False,
            'error': str(e),
        }


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantAdmin])
def upload_logo(request):
    """Upload tenant logo to S3."""
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file_obj = request.FILES['file']
    
    # Validate file type
    allowed_types = ['image/jpeg', 'image/png', 'image/svg+xml']
    if file_obj.content_type not in allowed_types:
        return Response(
            {'error': f'Invalid file type. Allowed: {allowed_types}'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (max 2MB)
    if file_obj.size > 2 * 1024 * 1024:
        return Response(
            {'error': 'File too large. Max 2MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tenant = request.tenant
    result = upload_to_spaces(file_obj, tenant.slug, 'logo')
    
    if not result['success']:
        return Response(
            {'error': result['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Update tenant settings
    settings_obj, _ = TenantSettings.objects.get_or_create(tenant=tenant)
    settings_obj.logo_url = result['url']
    settings_obj.save()
    
    return Response({
        'success': True,
        'url': result['url'],
        'message': 'Logo uploaded successfully'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsTenantAdmin])
def upload_favicon(request):
    """Upload tenant favicon to S3."""
    if 'file' not in request.FILES:
        return Response(
            {'error': 'No file provided'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    file_obj = request.FILES['file']
    
    # Validate file type
    allowed_types = ['image/png', 'image/x-icon', 'image/vnd.microsoft.icon']
    if file_obj.content_type not in allowed_types:
        return Response(
            {'error': f'Invalid file type. Allowed: PNG, ICO'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate file size (max 1MB)
    if file_obj.size > 1 * 1024 * 1024:
        return Response(
            {'error': 'File too large. Max 1MB'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    tenant = request.tenant
    result = upload_to_spaces(file_obj, tenant.slug, 'favicon')
    
    if not result['success']:
        return Response(
            {'error': result['error']},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Update tenant settings
    settings_obj, _ = TenantSettings.objects.get_or_create(tenant=tenant)
    settings_obj.favicon_url = result['url']
    settings_obj.save()
    
    return Response({
        'success': True,
        'url': result['url'],
        'message': 'Favicon uploaded successfully'
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsTenantAdmin])
def delete_asset(request, asset_type):
    """Delete logo or favicon from S3."""
    tenant = request.tenant
    
    try:
        settings_obj = TenantSettings.objects.get(tenant=tenant)
        
        if asset_type == 'logo':
            url = settings_obj.logo_url
            settings_obj.logo_url = ''
        elif asset_type == 'favicon':
            url = settings_obj.favicon_url
            settings_obj.favicon_url = ''
        else:
            return Response(
                {'error': 'Invalid asset type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not url:
            return Response(
                {'error': f'No {asset_type} to delete'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Delete from S3
        s3 = get_s3_client()
        bucket = settings.AWS_STORAGE_BUCKET_NAME
        s3_key = url.split(f"{bucket}/")[-1]
        
        try:
            s3.delete_object(Bucket=bucket, Key=s3_key)
        except ClientError:
            pass  # Ignore S3 errors, just clear the URL
        
        settings_obj.save()
        
        return Response({
            'success': True,
            'message': f'{asset_type} deleted successfully'
        })
        
    except TenantSettings.DoesNotExist:
        return Response(
            {'error': 'Settings not found'},
            status=status.HTTP_404_NOT_FOUND
        )
