---
name: project-model-geojson
description: Modelo Project com PostGIS PointField e PolygonField, serializer GeoJSON e endpoint de API para mapa.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Armazenar e expor a localização geográfica de projetos imobiliários usando PostGIS. O endpoint retorna GeoJSON válido para consumo direto por bibliotecas de mapas como Mapbox ou Leaflet.

## Code Pattern

```python
# projects/models.py
from django.contrib.gis.db import models as gis_models
from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=255)
    location_point = gis_models.PointField(
        srid=4326, null=True, blank=True,
        help_text="Coordenadas do centro do projeto (lon, lat)"
    )
    boundary_polygon = gis_models.PolygonField(
        srid=4326, null=True, blank=True,
        help_text="Polígono da área do projeto"
    )
    created_at = models.DateTimeField(auto_now_add=True)
```

```python
# projects/serializers.py
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework_gis.fields import GeometryField
from .models import Project

class ProjectGeoSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Project
        geo_field = "location_point"
        fields = ["id", "name", "location_point", "boundary_polygon"]

class ProjectMapSerializer(GeoFeatureModelSerializer):
    """Retorna FeatureCollection compatível com Mapbox."""
    class Meta:
        model = Project
        geo_field = "boundary_polygon"
        fields = ["id", "name", "boundary_polygon"]
```

```python
# projects/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Project
from .serializers import ProjectMapSerializer

class ProjectMapView(APIView):
    """GET /api/v1/projects/map/ — retorna GeoJSON FeatureCollection"""

    def get(self, request):
        projects = Project.objects.exclude(location_point=None)
        serializer = ProjectMapSerializer(projects, many=True)
        return Response({
            "type": "FeatureCollection",
            "features": serializer.data,
        })
```

```python
# settings.py — dependências necessárias
INSTALLED_APPS += ["django.contrib.gis"]
DATABASES["default"]["ENGINE"] = "django.contrib.gis.db.backends.postgis"
```

## Key Rules

- Usar sempre `srid=4326` (WGS84) para compatibilidade com APIs de mapas.
- Instalar `postgis` na base de dados: `CREATE EXTENSION postgis;`
- O `boundary_polygon` é opcional; usar `location_point` como fallback para o marcador no mapa.
- Adicionar índice espacial: `gis_models.PointField(..., spatial_index=True)`.

## Anti-Pattern

```python
# ERRADO: guardar coordenadas como FloatFields separados
latitude = models.FloatField()
longitude = models.FloatField()
# Perde-se suporte a queries espaciais (ST_Within, ST_Distance, etc.)
```
