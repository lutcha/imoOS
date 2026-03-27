---
name: penetration-test-checklist
description: Checklist de segurança pré-lançamento: bypass de autenticação, teste IDOR, XSS em descrições de unidades, injeção SQL via filtros, violação de isolamento de inquilino, bypass de rate limit e confusão de algoritmo JWT.
argument-hint: "[target_env]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Guia de testes de penetração focado nas vulnerabilidades específicas de uma aplicação SaaS multi-tenant imobiliária. Deve ser executado antes de cada lançamento major e após alterações significativas de segurança.

## Code Pattern

```bash
#!/bin/bash
# scripts/pentest_checklist.sh — documentação de testes manuais + automatizados

TARGET="${1:-https://staging.imoos.cv}"
echo "Alvo: $TARGET"
echo "Data: $(date)"

# ===== 1. BYPASS DE AUTENTICAÇÃO =====
echo "\n[1] Bypass de Autenticação"

# Testar acesso a endpoints protegidos sem token
curl -s "$TARGET/api/v1/inventory/units/" | python3 -c "
import sys, json
data = json.load(sys.stdin)
assert 'detail' in data or data.get('code') == 'not_authenticated', 'FALHA: Endpoint acessível sem auth!'
print('OK: Endpoint requer autenticação')
"

# Testar token expirado
curl -s -H "Authorization: Bearer eyJhbGciOiJIUzI1NiJ9.eyJleHAiOjF9.ASDF" \
  "$TARGET/api/v1/inventory/units/" | grep -q "token_not_valid" && echo "OK: Token expirado rejeitado"
```

```python
# tests/security/test_idor.py — Insecure Direct Object Reference
import pytest

@pytest.mark.security
@pytest.mark.django_db
class TestIDOR:
    def test_tenant_a_cannot_access_tenant_b_units(self, client):
        """IDOR: Utilizador do inquilino A não pode aceder às unidades do inquilino B."""
        from django_tenants.utils import schema_context

        with schema_context("tenant_a"):
            unit_a = UnitFactory()

        # Autenticar como utilizador do inquilino B
        with schema_context("tenant_b"):
            user_b = UserFactory()
            token = get_jwt_token(user_b)

        # Tentar aceder à unidade do inquilino A
        response = client.get(
            f"/api/v1/inventory/units/{unit_a.id}/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
            HTTP_HOST="tenant-b.imoos.cv",
        )
        assert response.status_code == 404, f"FALHA IDOR: Unidade de outro inquilino acessível! Status: {response.status_code}"

    def test_user_cannot_access_other_tenants_contracts(self, client):
        """IDOR: Verificar isolamento de contratos."""
        with schema_context("tenant_a"):
            contract_a = ContractFactory()
        with schema_context("tenant_b"):
            user_b = UserFactory()
            token = get_jwt_token(user_b)

        response = client.get(
            f"/api/v1/contracts/{contract_a.id}/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
            HTTP_HOST="tenant-b.imoos.cv",
        )
        assert response.status_code in [403, 404]
```

```python
# tests/security/test_xss.py — XSS em descrições de unidades
@pytest.mark.security
@pytest.mark.django_db
class TestXSS:
    XSS_PAYLOADS = [
        "<script>alert('xss')</script>",
        "javascript:alert(1)",
        "<img src=x onerror=alert(1)>",
        "';alert(String.fromCharCode(88,83,83))//",
    ]

    def test_unit_description_xss_sanitized(self, client, auth_token):
        for payload in self.XSS_PAYLOADS:
            response = client.post("/api/v1/inventory/units/", json={
                "description": payload, "code": "T1-001", "type": "T1", "area_bruta": "80.00"
            }, HTTP_AUTHORIZATION=f"Bearer {auth_token}")

            if response.status_code == 201:
                data = response.json()
                assert "<script>" not in data.get("description", ""), f"XSS não sanitizado: {payload}"
```

```python
# tests/security/test_sql_injection.py
@pytest.mark.security
class TestSQLInjection:
    SQL_PAYLOADS = ["' OR '1'='1", "'; DROP TABLE units; --", "1 UNION SELECT * FROM auth_user"]

    def test_unit_filter_sql_injection(self, client, auth_token):
        for payload in self.SQL_PAYLOADS:
            response = client.get(
                f"/api/v1/inventory/units/?type={payload}",
                HTTP_AUTHORIZATION=f"Bearer {auth_token}"
            )
            assert response.status_code in [200, 400], f"Status inesperado para payload SQL: {payload}"
            # 200 com lista vazia é OK; 500 indica vulnerabilidade
            if response.status_code == 200:
                assert "error" not in str(response.content).lower()
```

```python
# tests/security/test_jwt_algorithm_confusion.py
@pytest.mark.security
def test_jwt_algorithm_none_rejected(client):
    """Confusão de algoritmo: rejeitar tokens com alg=none."""
    import base64, json
    header = base64.urlsafe_b64encode(json.dumps({"alg": "none", "typ": "JWT"}).encode()).decode().rstrip("=")
    payload = base64.urlsafe_b64encode(json.dumps({"user_id": 1, "exp": 9999999999}).encode()).decode().rstrip("=")
    token = f"{header}.{payload}."  # sem assinatura

    response = client.get("/api/v1/inventory/units/", HTTP_AUTHORIZATION=f"Bearer {token}")
    assert response.status_code == 401, "FALHA: Token com alg=none aceite!"
```

## Key Rules

- Executar todos os testes marcados com `@pytest.mark.security` antes de cada lançamento para produção.
- O teste de isolamento de inquilino (`IDOR`) é o mais crítico num sistema multi-tenant — nunca omitir.
- Documentar falhas encontradas em issues privados antes de corrigir — nunca commitar "fix: security vulnerability" sem issue associado.
- Testar também com utilizadores de diferentes papéis: INVESTOR não deve ver dados de CRM.

## Anti-Pattern

```python
# ERRADO: testar segurança apenas na review de PR sem testes automatizados
# A segurança deve ser testada automaticamente em CI — revisão manual é insuficiente e inconsistente
```
