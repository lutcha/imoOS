"""
Projects module — Tenant schema.
Represents real estate developments (Empreendimentos).
"""
import uuid
from django.db import models
from django.contrib.gis.db import models as gis_models
from django.contrib.auth import get_user_model
from simple_history.models import HistoricalRecords

User = get_user_model()


from apps.core.models import TenantAwareModel

class Project(TenantAwareModel):
    """
    An Empreendimento — a real estate development project.
    """
    STATUS_PLANNING = 'PLANNING'
    STATUS_LICENSING = 'LICENSING'
    STATUS_CONSTRUCTION = 'CONSTRUCTION'
    STATUS_COMPLETED = 'COMPLETED'
    STATUS_CHOICES = [
        (STATUS_PLANNING, 'Em Planeamento'),
        (STATUS_LICENSING, 'Em Licenciamento'),
        (STATUS_CONSTRUCTION, 'Em Construção'),
        (STATUS_COMPLETED, 'Concluído'),
    ]

    name = models.CharField(max_length=200, verbose_name='Nome do Projecto')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PLANNING)

    # Location (PostGIS)
    location = gis_models.PointField(null=True, blank=True, srid=4326, help_text='Coordenadas GPS do projecto')
    land_parcel = gis_models.PolygonField(null=True, blank=True, srid=4326, help_text='Polígono do terreno')
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, default='Praia')
    island = models.CharField(max_length=50, default='Santiago')

    # Timeline
    start_date = models.DateField(null=True, blank=True)
    expected_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)

    # Team
    project_manager = models.ForeignKey(
        User, null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='managed_projects'
    )

    # Soft delete (is_deleted already handled if we want to inherit, 
    # but TenantAwareModel only has id, created_at, updated_at)
    is_deleted = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_projects')

    # Audit history
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Projecto'
        verbose_name_plural = 'Projectos'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Building(TenantAwareModel):
    """Edifício within a Project."""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='buildings')
    name = models.CharField(max_length=100)  # e.g., "Bloco A", "Torre 1"
    code = models.CharField(max_length=20)   # e.g., "BLK-A"
    floors_count = models.PositiveIntegerField(default=1)
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Edifício'
        verbose_name_plural = 'Edifícios'
        unique_together = ['project', 'code']

    def __str__(self):
        return f'{self.project.name} — {self.name}'


class Floor(TenantAwareModel):
    """Piso within a Building."""
    building = models.ForeignKey(Building, on_delete=models.CASCADE, related_name='floors')
    number = models.IntegerField()           # 0 = R/C, -1 = Cave, 1 = 1º andar
    name = models.CharField(max_length=50, blank=True)  # e.g., "Rés-do-Chão"
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Piso'
        verbose_name_plural = 'Pisos'
        unique_together = ['building', 'number']
        ordering = ['number']

    def __str__(self):
        return f'{self.building} — Piso {self.number}'


class ProjectDocument(TenantAwareModel):
    """
    Project Data Room Document
    Armazenamento e versionamento de plantas arquitetónicas, licenças e cadernos de encargos.
    """
    CATEGORY_PLAN = 'PLAN'
    CATEGORY_LICENSE = 'LICENSE'
    CATEGORY_CONTRACT = 'CONTRACT'
    CATEGORY_OTHER = 'OTHER'
    
    CATEGORY_CHOICES = [
        (CATEGORY_PLAN, 'Planta Arquitetónica'),
        (CATEGORY_LICENSE, 'Licença'),
        (CATEGORY_CONTRACT, 'Caderno de Encargos / Contrato'),
        (CATEGORY_OTHER, 'Outro')
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(upload_to='projects/documents/%Y/%m/', help_text='Ficheiro técnico')
    version = models.PositiveIntegerField(default=1)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_OTHER)
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_project_documents')
    
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Documento de Projecto'
        verbose_name_plural = 'Documentos de Projecto'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.get_category_display()} - v{self.version} ({self.project.name})'

    def save(self, *args, **kwargs):
        if self._state.adding:
            # Lógica de Versionamento: Encontrar o documento mais recente com a mesma categoria para este projecto
            latest_doc = ProjectDocument.objects.filter(project=self.project, category=self.category).order_by('-version').first()
            if latest_doc:
                self.version = latest_doc.version + 1
        super().save(*args, **kwargs)

