from django.db import models
from simple_history.models import HistoricalRecords
from apps.core.models import TenantAwareModel
from apps.inventory.models import Unit

class Lead(TenantAwareModel):
    STATUS_NEW = 'NEW'
    STATUS_CONTACTED = 'CONTACTED'
    STATUS_QUALIFIED = 'QUALIFIED'
    STATUS_LOST = 'LOST'
    STATUS_CONVERTED = 'CONVERTED'
    
    STATUS_CHOICES = [
        (STATUS_NEW, 'Novo'),
        (STATUS_CONTACTED, 'Contactado'),
        (STATUS_QUALIFIED, 'Qualificado'),
        (STATUS_LOST, 'Perdido'),
        (STATUS_CONVERTED, 'Convertido (Venda)'),
    ]

    SOURCE_WEB = 'WEB'
    SOURCE_INSTAGRAM = 'INSTAGRAM'
    SOURCE_FACEBOOK = 'FACEBOOK'
    SOURCE_REFERRAL = 'REFERRAL'
    SOURCE_OTHER = 'OTHER'
    
    SOURCE_CHOICES = [
        (SOURCE_WEB, 'Website'),
        (SOURCE_INSTAGRAM, 'Instagram'),
        (SOURCE_FACEBOOK, 'Facebook'),
        (SOURCE_REFERRAL, 'Referência'),
        (SOURCE_OTHER, 'Outro'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_NEW)
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default=SOURCE_WEB)
    
    budget = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    preferred_typology = models.CharField(max_length=10, blank=True)  # T1, T2 etc.
    
    notes = models.TextField(blank=True)
    
    assigned_to = models.ForeignKey(
        'users.User', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_leads'
    )
    
    # Interest
    interested_unit = models.ForeignKey(
        Unit, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='leads'
    )

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Lead'
        verbose_name_plural = 'Leads'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.status})'

class Interaction(TenantAwareModel):
    TYPE_CALL = 'CALL'
    TYPE_MEETING = 'MEETING'
    TYPE_EMAIL = 'EMAIL'
    TYPE_WHATSAPP = 'WHATSAPP'
    TYPE_CHOICES = [
        (TYPE_CALL, 'Chamada'),
        (TYPE_MEETING, 'Reunião'),
        (TYPE_EMAIL, 'E-mail'),
        (TYPE_WHATSAPP, 'WhatsApp'),
    ]

    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateTimeField()
    summary = models.TextField()
    is_completed = models.BooleanField(default=True)
    
    created_by = models.ForeignKey('users.User', on_delete=models.CASCADE)

    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Interação'
        verbose_name_plural = 'Interações'
        ordering = ['-date']
