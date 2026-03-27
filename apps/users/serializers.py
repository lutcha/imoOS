from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import connection
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)

        # Inject tenant_schema from active connection (django-tenants middleware)
        token['tenant_schema'] = connection.schema_name
        token['tenant_name'] = getattr(connection.tenant, 'name', 'Public')
        token['email'] = user.email
        token['role'] = user.role
        token['full_name'] = user.get_full_name() or user.email
        token['is_staff'] = user.is_staff  # Sprint 7: Super-admin access

        return token

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        # Expose tenant_schema and user info in response body for frontend
        data['tenant_schema'] = refresh.get('tenant_schema')
        data['tenant_name'] = refresh.get('tenant_name')
        data['user'] = UserSerializer(self.user).data

        return data
