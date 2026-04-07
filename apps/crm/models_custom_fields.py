"""
Custom Fields for CRM Leads
Allows tenants to define custom fields for their leads
"""
import uuid
from django.db import models
from apps.core.models import TenantAwareModel


class CustomFieldDefinition(TenantAwareModel):
    """
    Definition of a custom field that can be added to leads.
    Examples: 'NIF', 'Profissão', 'Rendimento Anual', etc.
    """
    FIELD_TYPES = [
        ('text', 'Texto'),
        ('number', 'Número'),
        ('date', 'Data'),
        ('boolean', 'Sim/Não'),
        ('choice', 'Escolha'),
        ('email', 'Email'),
        ('phone', 'Telefone'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Nome do Campo")
    key = models.SlugField(max_length=50, verbose_name="Chave (identifier)")
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES, verbose_name="Tipo")
    required = models.BooleanField(default=False, verbose_name="Obrigatório")
    help_text = models.CharField(max_length=200, blank=True, verbose_name="Ajuda")
    choices = models.JSONField(default=list, blank=True, verbose_name="Opções (para tipo Escolha)")
    order = models.PositiveIntegerField(default=0, verbose_name="Ordem")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    
    class Meta:
        verbose_name = "Campo Personalizado"
        verbose_name_plural = "Campos Personalizados"
        ordering = ['order', 'name']
        unique_together = ['tenant', 'key']
    
    def __str__(self):
        return f"{self.name} ({self.get_field_type_display()})"


class LeadCustomValue(TenantAwareModel):
    """
    Value of a custom field for a specific lead.
    """
    lead = models.ForeignKey('Lead', on_delete=models.CASCADE, related_name='custom_values')
    field = models.ForeignKey(CustomFieldDefinition, on_delete=models.CASCADE)
    value_text = models.TextField(blank=True, null=True)
    value_number = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    value_date = models.DateField(blank=True, null=True)
    value_boolean = models.BooleanField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Valor de Campo Personalizado"
        verbose_name_plural = "Valores de Campos Personalizados"
        unique_together = ['lead', 'field']
    
    @property
    def value(self):
        """Return the appropriate value based on field type."""
        field_type = self.field.field_type
        if field_type == 'text':
            return self.value_text
        elif field_type == 'number':
            return self.value_number
        elif field_type == 'date':
            return self.value_date
        elif field_type == 'boolean':
            return self.value_boolean
        elif field_type in ['choice', 'email', 'phone']:
            return self.value_text
        return None
    
    def set_value(self, value):
        """Set the appropriate value field based on field type."""
        field_type = self.field.field_type
        if field_type == 'text':
            self.value_text = value
        elif field_type == 'number':
            self.value_number = value
        elif field_type == 'date':
            self.value_date = value
        elif field_type == 'boolean':
            self.value_boolean = value
        elif field_type in ['choice', 'email', 'phone']:
            self.value_text = value
