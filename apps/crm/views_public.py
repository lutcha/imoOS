from django.db import connection
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.core.throttling import PublicEndpointThrottle
from .serializers import PublicLeadSerializer


class LeadCaptureView(generics.CreateAPIView):
    """
    Public-facing endpoint to capture leads from external sources (Web, Instagram, etc.)
    Uses PublicLeadSerializer — no assigned_to / interested_unit writable fields.
    Rate limited to 100 req/hour per IP (CLAUDE.md security rule).

    After saving, triggers notify_whatsapp_new_lead asynchronously so the
    sales team receives an immediate WhatsApp notification.
    """
    serializer_class = PublicLeadSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicEndpointThrottle]

    def perform_create(self, serializer):
        from .tasks import notify_whatsapp_new_lead

        lead = serializer.save()
        notify_whatsapp_new_lead.delay(
            tenant_schema=connection.schema_name,
            lead_id=str(lead.id),
        )


class WhatsAppWebhookView(APIView):
    """
    WhatsApp Cloud API webhook — Meta verification + delivery status updates.
    Full implementation: Sprint 6 prompt 05-whatsapp-automation.md
    """
    permission_classes = [AllowAny]
    throttle_classes = [PublicEndpointThrottle]

    def get(self, request, *args, **kwargs):
        """Meta hub verification challenge."""
        mode = request.query_params.get('hub.mode')
        challenge = request.query_params.get('hub.challenge')
        verify_token = request.query_params.get('hub.verify_token')
        from django.conf import settings
        expected = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', '')
        if mode == 'subscribe' and verify_token == expected:
            return Response(int(challenge) if challenge and challenge.isdigit() else challenge)
        return Response({'detail': 'Forbidden'}, status=403)

    def post(self, request, *args, **kwargs):
        """Receive delivery status + opt-out events (async processing — Sprint 6)."""
        return Response({'status': 'received'})
