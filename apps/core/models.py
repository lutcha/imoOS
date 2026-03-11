import uuid
from django.db import models
from simple_history.models import HistoricalRecords

class BaseModel(models.Model):
    """
    Base abstraction for all business models.
    Provides UUID primary key and standard audit timestamps.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Criado em')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Actualizado em')

    # Audit History (mandatory for transactional models)
    # Subclasses should add history = HistoricalRecords() or it can be inherited 
    # but some models might not need it.
    
    class Meta:
        abstract = True

class TenantAwareModel(BaseModel):
    """
    Base model for any model that should be tenant-isolated.
    Note: django-tenants handles schema isolation, so this is mostly 
    for consistency and potential future filtering or logic.
    """
    # history = HistoricalRecords(inherit=True)  # Can be problematic in abstract models sometimes
    
    class Meta:
        abstract = True
