from rest_framework import generics
from rest_framework.permissions import AllowAny
from apps.core.throttling import PublicEndpointThrottle
from .serializers import PublicLeadSerializer

class LeadCaptureView(generics.CreateAPIView):
    """
    Public-facing endpoint to capture leads from external sources (Web, Instagram, etc.)
    Uses PublicLeadSerializer — no assigned_to / interested_unit writable fields.
    Rate limited to 100 req/hour per IP (CLAUDE.md security rule).
    """
    serializer_class = PublicLeadSerializer
    permission_classes = [AllowAny]
    throttle_classes = [PublicEndpointThrottle]

    def perform_create(self, serializer):
        # Additional logic can be added here (e.g., sending notification emails)
        serializer.save()
