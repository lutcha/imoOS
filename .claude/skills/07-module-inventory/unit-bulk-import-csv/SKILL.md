---
name: unit-bulk-import-csv
description: Importação de unidades via CSV (code,type,area_bruta,price_cve), task Celery assíncrona, endpoint de pré-visualização (validar sem guardar) e reporte de erros por linha.
argument-hint: "[project_id] [csv_file_path]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Permitir a importação em massa de unidades a partir de ficheiros CSV. O endpoint de preview valida os dados sem os persistir, devolvendo erros por linha para o utilizador corrigir antes da importação final.

## Code Pattern

```python
# inventory/views.py
import csv
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .tasks import import_units_from_csv
from .validators import validate_unit_csv_row

class UnitCSVPreviewView(APIView):
    """POST /api/v1/inventory/units/csv-preview/ — valida sem guardar"""
    parser_classes = [MultiPartParser]

    def post(self, request, project_id):
        csv_file = request.FILES.get("file")
        if not csv_file:
            return Response({"error": "Ficheiro CSV obrigatório."}, status=400)

        content = csv_file.read().decode("utf-8-sig")
        reader = csv.DictReader(io.StringIO(content))
        results = []

        for i, row in enumerate(reader, start=2):  # linha 1 = cabeçalho
            errors = validate_unit_csv_row(row)
            results.append({
                "row": i,
                "data": row,
                "valid": len(errors) == 0,
                "errors": errors,
            })

        valid_count = sum(1 for r in results if r["valid"])
        return Response({
            "total": len(results),
            "valid": valid_count,
            "invalid": len(results) - valid_count,
            "rows": results,
        })
```

```python
# inventory/validators.py
from decimal import Decimal, InvalidOperation

REQUIRED_COLUMNS = {"code", "type", "area_bruta", "price_cve"}
VALID_TYPES = {"T0", "T1", "T2", "T3", "T4", "COMMERCIAL", "PARKING"}

def validate_unit_csv_row(row: dict) -> list[str]:
    errors = []
    missing = REQUIRED_COLUMNS - set(row.keys())
    if missing:
        errors.append(f"Colunas em falta: {missing}")
        return errors

    if not row["code"].strip():
        errors.append("Código não pode estar vazio.")
    if row["type"].upper() not in VALID_TYPES:
        errors.append(f"Tipo '{row['type']}' inválido. Use: {VALID_TYPES}")
    try:
        area = Decimal(row["area_bruta"])
        if area <= 0:
            errors.append("area_bruta deve ser maior que zero.")
    except InvalidOperation:
        errors.append(f"area_bruta '{row['area_bruta']}' não é um número válido.")
    try:
        price = Decimal(row["price_cve"])
        if price <= 0:
            errors.append("price_cve deve ser maior que zero.")
    except InvalidOperation:
        errors.append(f"price_cve '{row['price_cve']}' não é um número válido.")

    return errors
```

```python
# inventory/tasks.py
from celery import shared_task

@shared_task(bind=True)
def import_units_from_csv(self, project_id: int, s3_key: str, user_id: int):
    """Task assíncrona para importação após validação aprovada."""
    import boto3, csv, io
    from .models import Unit
    from .services import create_unit_with_pricing

    s3 = boto3.client("s3")
    content = s3.get_object(Bucket="imoos-imports", Key=s3_key)["Body"].read().decode()
    reader = csv.DictReader(io.StringIO(content))
    errors = []

    for i, row in enumerate(reader, start=2):
        try:
            create_unit_with_pricing(project_id=project_id, data=row)
        except Exception as e:
            errors.append({"row": i, "error": str(e)})

    return {"imported": i - len(errors), "errors": errors}
```

## Key Rules

- O endpoint de preview nunca deve persistir dados — usar transações com rollback ou simplesmente não chamar `.save()`.
- Fazer upload do CSV para S3 antes de disparar a task Celery, passando o `s3_key` como argumento.
- Reportar erros com número de linha e descrição clara para facilitar a correção pelo utilizador.
- Aceitar separador `;` além de `,` para compatibilidade com Excel em português.

## Anti-Pattern

```python
# ERRADO: processar CSV de forma síncrona no request — timeout para ficheiros grandes
for row in csv.DictReader(large_file):
    Unit.objects.create(**row)  # bloqueia o request durante minutos
```
