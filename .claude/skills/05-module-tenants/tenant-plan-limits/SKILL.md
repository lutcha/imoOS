---
name: tenant-plan-limits
description: Aplicação de quotas por plano (max_units, max_users, max_projects) com decorator ou sinal pre-save. Lança TenantQuotaExceededException (HTTP 402).
argument-hint: "[resource_type]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir que cada inquilino não excede os limites do seu plano de subscrição. A verificação deve acontecer antes de criar novos recursos, com retorno de erro HTTP 402 (Payment Required) para o cliente.

## Code Pattern

```python
# tenants/exceptions.py
from rest_framework.exceptions import APIException

class TenantQuotaExceededException(APIException):
    status_code = 402
    default_code = "quota_exceeded"

    def __init__(self, resource: str, limit: int):
        self.detail = (
            f"Limite do plano atingido: não é possível criar mais {resource}. "
            f"Limite atual: {limit}. Faça upgrade do plano."
        )
```

```python
# tenants/decorators.py
from functools import wraps
from .models import TenantSettings
from .exceptions import TenantQuotaExceededException

def check_quota(resource: str, count_fn):
    """
    resource: 'unidades' | 'utilizadores' | 'projetos'
    count_fn: callable que retorna o total atual do recurso
    """
    def decorator(func):
        @wraps(func)
        def wrapper(request, *args, **kwargs):
            settings = TenantSettings.objects.get()
            limit_map = {
                "unidades": settings.max_units,
                "utilizadores": settings.max_users,
                "projetos": settings.max_projects,
            }
            limit = limit_map[resource]
            current = count_fn()
            if current >= limit:
                raise TenantQuotaExceededException(resource, limit)
            return func(request, *args, **kwargs)
        return wrapper
    return decorator
```

```python
# inventory/views.py
from units.models import Unit
from tenants.decorators import check_quota

@check_quota("unidades", count_fn=lambda: Unit.objects.count())
def create_unit(request):
    ...
```

```python
# Alternativa: sinal pre_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from units.models import Unit

@receiver(pre_save, sender=Unit)
def enforce_unit_quota(sender, instance, **kwargs):
    if instance.pk:  # atualização, não criação
        return
    settings = TenantSettings.objects.get()
    if Unit.objects.count() >= settings.max_units:
        raise TenantQuotaExceededException("unidades", settings.max_units)
```

## Key Rules

- Retornar sempre HTTP 402 (não 400 nem 403) para erros de quota excedida.
- Verificar quotas antes de qualquer operação de escrita, nunca depois.
- O `count_fn` deve contar apenas recursos ativos (excluir registos arquivados/eliminados).
- Cachear `TenantSettings` em Redis para evitar queries repetidas em endpoints de alto volume.

## Anti-Pattern

```python
# ERRADO: verificar quota após criar o objeto — pode causar dados inconsistentes
unit = Unit.objects.create(...)
if Unit.objects.count() > settings.max_units:
    unit.delete()  # race condition possível
    raise TenantQuotaExceededException(...)
```
