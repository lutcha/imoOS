from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import connection
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined']
        read_only_fields = ['id', 'date_joined']

class TenantTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user: User):
        token = super().get_token(user)
        
        # Inject tenant_schema from active connection (django-tenants middleware)
        token['tenant_schema'] = connection.schema_name
        token['tenant_name'] = getattr(connection.tenant, 'name', 'Public')
        token['user_email'] = user.email
        token['user_role'] = user.role
        
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        refresh = self.get_token(self.user)
        
        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        # Add user info to response
        data['user'] = UserSerializer(self.user).data
        
        return data
