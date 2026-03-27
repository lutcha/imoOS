from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from apps.tenants.permissions import IsTenantAdmin
from .models import TenantMembership
from .serializers import TenantMembershipSerializer


class MembershipViewSet(viewsets.ModelViewSet):
    """
    Manage which users belong to this tenant and what role they hold.
    List/read: any authenticated tenant member.
    Create/update/delete: tenant admin only.
    """
    serializer_class = TenantMembershipSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active']
    ordering_fields = ['created_at', 'role']

    def get_queryset(self):
        return TenantMembership.objects.select_related('user').order_by('created_at')

    def get_permissions(self):
        if self.action in ('list', 'retrieve'):
            return [IsAuthenticated()]
        return [IsAuthenticated(), IsTenantAdmin()]
