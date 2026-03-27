from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django.http import Http404
from django.db import connection

from apps.core.throttling import PublicEndpointThrottle
from apps.contracts.models import SignatureRequest

class SignatureView(APIView):
    """
    Public-facing endpoint for contract signing.
    No authentication required, rate-limited per IP.
    """
    permission_classes = []
    throttle_classes = [PublicEndpointThrottle]

    def get_signature_request_or_404(self, token: str) -> SignatureRequest:
        try:
            sr = SignatureRequest.objects.select_related('contract__lead', 'contract__unit').get(
                token=token, status=SignatureRequest.STATUS_PENDING,
            )
        except SignatureRequest.DoesNotExist:
            raise Http404
        if sr.is_expired:
            sr.status = SignatureRequest.STATUS_EXPIRED
            sr.save(update_fields=['status'])
            raise ValidationError({'detail': 'Link de assinatura expirado.'})
        return sr

    def get(self, request, token):
        sr = self.get_signature_request_or_404(token)
        contract = sr.contract
        return Response({
            'contract_number': contract.contract_number,
            'lead_name': f"{contract.lead.first_name} {contract.lead.last_name}",
            'unit_code': contract.unit.code,
            'total_price_cve': contract.total_price_cve,
            'expires_at': sr.expires_at,
        })

    def post(self, request, token):
        import base64
        import boto3
        from django.conf import settings
        from django.utils import timezone
        from apps.contracts.tasks import finalize_signed_contract

        sr = self.get_signature_request_or_404(token)
        
        signature_png_base64 = request.data.get('signature_png_base64')
        signed_by_name = request.data.get('signed_by_name')

        if not signature_png_base64 or not signed_by_name:
            return Response(
                {'detail': 'signature_png_base64 e signed_by_name são obrigatórios.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        tenant_slug = connection.tenant.slug
        s3_key = f'tenants/{tenant_slug}/signatures/{sr.token}.png'

        try:
            # decode base64 assuming it's correctly formatted and without 'data:image/png;base64,' prefix 
            # (frontend sends it cleaned)
            image_data = base64.b64decode(signature_png_base64)
            s3 = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                endpoint_url=getattr(settings, 'AWS_S3_ENDPOINT_URL', None) or None,
                region_name='us-east-1',
            )
            s3.put_object(
                Bucket=settings.AWS_STORAGE_BUCKET_NAME,
                Key=s3_key,
                Body=image_data,
                ContentType='image/png',
                ServerSideEncryption='AES256',
            )
        except Exception as exc:
            return Response(
                {'detail': 'Falha ao guardar assinatura no S3.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        sr.signature_png_s3_key = s3_key
        sr.signed_by_name = signed_by_name
        sr.signed_at = timezone.now()
        sr.ip_address = request.META.get('REMOTE_ADDR')
        sr.status = SignatureRequest.STATUS_SIGNED
        sr.save(update_fields=['signature_png_s3_key', 'signed_by_name', 'signed_at', 'ip_address', 'status'])
        
        finalize_signed_contract.delay(
            tenant_schema=connection.schema_name,
            signature_request_id=str(sr.id),
        )

        return Response({'detail': 'Contrato assinado com sucesso.'}, status=status.HTTP_200_OK)
