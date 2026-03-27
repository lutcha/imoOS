---
name: daily-log-offline-sync
description: Modelo DailyLog (date/project/work_done/workers_count/weather), endpoint de sincronização que aceita array de registos locais e resolução de conflitos server-wins.
argument-hint: "[project_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir que equipas no campo registem diários de obra sem cobertura de rede. Ao recuperar a ligação, o dispositivo envia um array de registos locais. Em caso de conflito (mesmo projeto + data), o servidor prevalece.

## Code Pattern

```python
# construction/models.py
from django.db import models

class WeatherCondition(models.TextChoices):
    CLEAR = "CLEAR", "Sol"
    CLOUDY = "CLOUDY", "Nublado"
    RAIN = "RAIN", "Chuva"
    HEAVY_RAIN = "HEAVY_RAIN", "Chuva Forte"
    WIND = "WIND", "Vento Forte"

class DailyLog(models.Model):
    project = models.ForeignKey("projects.Project", on_delete=models.CASCADE, related_name="daily_logs")
    date = models.DateField()
    work_done = models.TextField()
    workers_count = models.PositiveIntegerField(default=0)
    weather = models.CharField(max_length=20, choices=WeatherCondition.choices, default=WeatherCondition.CLEAR)
    equipment_used = models.TextField(blank=True)
    issues = models.TextField(blank=True)
    created_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True)
    local_id = models.CharField(max_length=36, blank=True, db_index=True)  # UUID gerado offline
    synced_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "date")
```

```python
# construction/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from django.db import transaction

class DailyLogSyncView(APIView):
    """POST /api/v1/construction/daily-logs/sync/"""

    def post(self, request):
        records = request.data.get("records", [])
        if not isinstance(records, list):
            return Response({"error": "records deve ser um array."}, status=400)

        results = []
        for record in records:
            result = self._sync_record(record, request.user)
            results.append(result)

        return Response({
            "synced": sum(1 for r in results if r["action"] != "conflict"),
            "conflicts": sum(1 for r in results if r["action"] == "conflict"),
            "results": results,
        })

    @transaction.atomic
    def _sync_record(self, record: dict, user) -> dict:
        from .models import DailyLog
        from .serializers import DailyLogSerializer

        project_id = record.get("project")
        date = record.get("date")
        local_id = record.get("local_id", "")

        existing = DailyLog.objects.filter(project_id=project_id, date=date).first()

        if existing:
            # Conflito: servidor prevalece (server-wins)
            return {
                "local_id": local_id,
                "action": "conflict",
                "server_record": DailyLogSerializer(existing).data,
                "message": f"Registo de {date} já existe no servidor. Dados locais descartados.",
            }

        # Não existe: criar registo
        serializer = DailyLogSerializer(data={**record, "created_by": user.id})
        serializer.is_valid(raise_exception=False)
        if serializer.is_valid():
            log = serializer.save(created_by=user)
            return {"local_id": local_id, "action": "created", "server_id": log.id}
        return {"local_id": local_id, "action": "error", "errors": serializer.errors}
```

## Key Rules

- Em caso de conflito (mesmo projeto + data), o servidor sempre prevalece — retornar o registo do servidor para o dispositivo atualizar.
- O `local_id` (UUID gerado offline) é essencial para o dispositivo correlacionar respostas com registos locais.
- O `unique_together = ("project", "date")` na base de dados garante que a política server-wins é aplicada mesmo em acessos concorrentes.
- Aceitar arrays de até 100 registos por chamada — rejeitar lotes maiores com HTTP 413.

## Anti-Pattern

```python
# ERRADO: usar last-write-wins por timestamp local — timestamp do dispositivo pode ser incorreto
if record["updated_at"] > existing.synced_at:  # relógio do dispositivo pode estar errado
    existing.update(**record)
```
