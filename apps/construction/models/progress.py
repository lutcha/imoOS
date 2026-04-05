"""
Progress tracking - Fotos e logs de progresso das tasks
"""
from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel


class TaskPhoto(TenantAwareModel):
    """
    Fotos da obra ligadas a tasks.
    Inclui geolocalização e metadados EXIF.
    """
    
    task = models.ForeignKey(
        'construction.ConstructionTask',
        on_delete=models.CASCADE,
        related_name='photos',
        verbose_name='Tarefa'
    )
    uploaded_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='uploaded_task_photos',
        verbose_name='Carregado por'
    )
    
    # Imagem (S3)
    image = models.ImageField(
        upload_to='construction/photos/%Y/%m/',
        verbose_name='Imagem'
    )
    thumbnail = models.ImageField(
        upload_to='construction/photos/%Y/%m/thumbs/',
        null=True,
        blank=True,
        verbose_name='Miniatura'
    )
    
    caption = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Legenda'
    )
    
    # Geolocalização
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Latitude'
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        verbose_name='Longitude'
    )
    
    # Metadados EXIF
    taken_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Data da Foto (EXIF)'
    )
    
    # Progresso no momento da foto
    progress_at_upload = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name='Progresso no Momento'
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Carregado em'
    )
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Foto da Tarefa'
        verbose_name_plural = 'Fotos das Tarefas'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['task', '-uploaded_at']),
            models.Index(fields=['uploaded_by', '-uploaded_at']),
        ]
    
    def __str__(self):
        return f'Foto {self.id} - {self.task.name}'
    
    @property
    def has_geotag(self):
        """Retorna True se tem coordenadas GPS."""
        return self.latitude is not None and self.longitude is not None
    
    def extract_exif(self):
        """Extrair metadados EXIF da imagem (chamar após upload)."""
        try:
            from PIL import Image
            from PIL.ExifTags import TAGS, GPSTAGS
            
            img = Image.open(self.image)
            exif = img._getexif()
            
            if not exif:
                return
            
            # Extrair data
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                
                if tag == 'DateTimeOriginal' and not self.taken_at:
                    from datetime import datetime
                    try:
                        self.taken_at = datetime.strptime(value, '%Y:%m:%d %H:%M:%S')
                    except ValueError:
                        pass
                
                # Extrair GPS
                if tag == 'GPSInfo':
                    gps_data = {}
                    for key in value.keys():
                        decode = GPSTAGS.get(key, key)
                        gps_data[decode] = value[key]
                    
                    # Converter para decimal
                    if 'GPSLatitude' in gps_data and 'GPSLongitude' in gps_data:
                        lat = self._convert_gps_coords(
                            gps_data['GPSLatitude'],
                            gps_data.get('GPSLatitudeRef', 'N')
                        )
                        lon = self._convert_gps_coords(
                            gps_data['GPSLongitude'],
                            gps_data.get('GPSLongitudeRef', 'E')
                        )
                        self.latitude = lat
                        self.longitude = lon
        
        except Exception:
            # Silenciar erros de EXIF
            pass
    
    def _convert_gps_coords(self, coords, ref):
        """Converter coordenadas GPS para decimal."""
        degrees = coords[0]
        minutes = coords[1]
        seconds = coords[2]
        
        decimal = float(degrees) + float(minutes) / 60 + float(seconds) / 3600
        
        if ref in ['S', 'W']:
            decimal = -decimal
        
        return decimal
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        if is_new:
            self.extract_exif()
            # Re-salvar com dados EXIF
            super().save(update_fields=['taken_at', 'latitude', 'longitude'])


class TaskProgressLog(TenantAwareModel):
    """
    Log de alterações de progresso - timeline da task.
    """
    
    task = models.ForeignKey(
        'construction.ConstructionTask',
        on_delete=models.CASCADE,
        related_name='progress_logs',
        verbose_name='Tarefa'
    )
    updated_by = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='progress_updates'
    )
    
    # Valores
    old_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Progresso Anterior'
    )
    new_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Novo Progresso'
    )
    
    # Notas
    notes = models.TextField(
        blank=True,
        verbose_name='Notas'
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data'
    )
    
    class Meta:
        app_label = 'construction'
        verbose_name = 'Log de Progresso'
        verbose_name_plural = 'Logs de Progresso'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', '-created_at']),
        ]
    
    def __str__(self):
        return f'{self.task.name}: {self.old_percent}% → {self.new_percent}%'
    
    @property
    def delta(self):
        """Diferença de progresso."""
        return self.new_percent - self.old_percent
