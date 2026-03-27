import re
from django.db import transaction
from rest_framework import serializers
from .models import Client, Domain, TenantSettings


class DomainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Domain
        fields = ('id', 'domain', 'is_primary')
        read_only_fields = ('id',)


class TenantSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TenantSettings
        fields = (
            'logo_url', 'primary_color',
            'max_projects', 'max_units', 'max_users',
            'imo_cv_api_key', 'whatsapp_phone_id',
        )
        # Plan limits are set at provisioning time, not by tenant admins.
        # API keys are write-only — never returned in read responses.
        read_only_fields = ('max_projects', 'max_units', 'max_users')
        extra_kwargs = {
            'imo_cv_api_key': {'write_only': True},
            'whatsapp_phone_id': {'write_only': True},
        }


class TenantSettingsWritableSerializer(TenantSettingsSerializer):
    """Staff-only: exposes plan limit fields as writable."""
    class Meta(TenantSettingsSerializer.Meta):
        read_only_fields = ()


class ClientSerializer(serializers.ModelSerializer):
    settings = TenantSettingsSerializer(read_only=True)
    domains = DomainSerializer(many=True, read_only=True)
    s3_prefix = serializers.CharField(read_only=True)

    class Meta:
        model = Client
        fields = (
            'id', 'name', 'slug', 'schema_name', 'plan', 'is_active',
            'country', 'currency', 'timezone',
            's3_prefix', 'settings', 'domains',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'schema_name', 's3_prefix', 'created_at', 'updated_at')


class ClientCreateSerializer(serializers.ModelSerializer):
    """
    Used for POST /admin/tenants/ — creates Client + primary Domain + TenantSettings
    in a single request. Schema creation is handled by django-tenants
    (auto_create_schema=True) when the Client is saved.
    """
    domain = serializers.CharField(
        write_only=True,
        help_text='Primary domain (e.g. empresa-a.imos.cv)',
    )

    class Meta:
        model = Client
        fields = (
            'name', 'slug', 'schema_name', 'plan',
            'country', 'currency', 'timezone', 'domain',
        )

    def validate_schema_name(self, value):
        if not re.match(r'^[a-z][a-z0-9_]*$', value):
            raise serializers.ValidationError(
                'Must be lowercase letters/digits/underscores, starting with a letter.'
            )
        if Client.objects.filter(schema_name=value).exists():
            raise serializers.ValidationError('Schema name already in use.')
        return value

    def validate_slug(self, value):
        if Client.objects.filter(slug=value).exists():
            raise serializers.ValidationError('Slug already in use.')
        return value

    def validate_domain(self, value):
        if Domain.objects.filter(domain=value).exists():
            raise serializers.ValidationError('Domain already in use.')
        return value

    def create(self, validated_data):
        domain_name = validated_data.pop('domain')
        # atomic() ensures the Client row and Domain row are rolled back together
        # if either step fails. The PostgreSQL schema DDL (triggered by
        # auto_create_schema=True) cannot be rolled back, but the Client row
        # removal prevents dead-schema routing issues.
        with transaction.atomic():
            client = Client.objects.create(**validated_data)
            Domain.objects.create(domain=domain_name, tenant=client, is_primary=True)
            TenantSettings.objects.get_or_create(tenant=client)
        return client
