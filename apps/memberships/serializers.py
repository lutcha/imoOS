from rest_framework import serializers
from .models import TenantMembership


class TenantMembershipSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = TenantMembership
        fields = ('id', 'user', 'user_email', 'role', 'is_active', 'created_at', 'updated_at')
        read_only_fields = ('id', 'created_at', 'updated_at')
