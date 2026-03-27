---
name: error-handling-drf
description: Standardized API error responses for ImoOS — consistent {error: {code, message, details}} format. Auto-load when implementing custom exception handling or writing error responses.
argument-hint: [error-type] [module]
allowed-tools: Read, Write
---

# DRF Error Handling — ImoOS

## Custom Exception Handler
```python
# apps/core/exceptions.py
from rest_framework.views import exception_handler
from rest_framework import status
import logging

logger = logging.getLogger('imos.api')

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        tenant = getattr(context['request'], 'tenant', None)
        logger.error(
            'API error',
            extra={
                'tenant': tenant.schema_name if tenant else None,
                'user': context['request'].user.id if context['request'].user.is_authenticated else None,
                'path': context['request'].path,
                'status': response.status_code,
                'error': str(exc),
            }
        )
        response.data = {
            'error': {
                'code': _get_error_code(exc),
                'message': _get_error_message(exc, response),
                'details': response.data,
            }
        }
    return response

def _get_error_code(exc):
    from rest_framework.exceptions import (
        ValidationError, AuthenticationFailed, NotAuthenticated,
        PermissionDenied, NotFound, Throttled,
    )
    mapping = {
        ValidationError: 'VALIDATION_ERROR',
        AuthenticationFailed: 'AUTH_FAILED',
        NotAuthenticated: 'NOT_AUTHENTICATED',
        PermissionDenied: 'PERMISSION_DENIED',
        NotFound: 'NOT_FOUND',
        Throttled: 'RATE_LIMITED',
    }
    return mapping.get(type(exc), 'SERVER_ERROR')
```

## Custom Business Exceptions
```python
from rest_framework.exceptions import APIException

class UnitAlreadyReservedException(APIException):
    status_code = 409
    default_code = 'UNIT_ALREADY_RESERVED'
    default_detail = 'Esta unidade já foi reservada. Por favor, escolha outra.'

class TenantQuotaExceededException(APIException):
    status_code = 402
    default_code = 'QUOTA_EXCEEDED'
    default_detail = 'Limite do plano atingido. Faça upgrade para continuar.'
```

## Response Format Examples
```json
// Validation error
{"error": {"code": "VALIDATION_ERROR", "message": "Dados inválidos.", "details": {"price_cve": ["Este campo é obrigatório."]}}}

// Not found
{"error": {"code": "NOT_FOUND", "message": "Não encontrado.", "details": null}}

// Business rule violation
{"error": {"code": "UNIT_ALREADY_RESERVED", "message": "Esta unidade já foi reservada.", "details": null}}
```

## Key Rules
- All error responses follow `{error: {code, message, details}}` — never bare DRF format
- Log every 5xx with tenant context for Sentry grouping
- Business rule violations use 409 Conflict, not 400 Bad Request
- Translate error messages to `pt-PT` for user-facing display
