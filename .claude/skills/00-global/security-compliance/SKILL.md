---
name: security-compliance
description: Apply ImoOS security rules — Lei 133/V/2019 (Cabo Verde LGPD), OWASP Top 10 prevention, audit logging. Auto-load when handling personal data, auth flows, or financial operations.
argument-hint: [feature] [risk-level]
allowed-tools: Read, Grep
---

# ImoOS Security & Compliance

## Data Protection — Lei n.º 133/V/2019 (Cabo Verde)
Equivalent to GDPR. Requirements:

- **Consent tracking**: `consent_marketing` + `consent_data_processing` fields on Buyer model
- **Right to erasure**: management command to anonymize PII (keep financial records per fiscal law)
- **Data portability**: export buyer data as structured JSON/CSV on request
- **Access logging**: `audit_logs` table must record who accessed personal data and when
- **Breach notification**: process documented, notify CNPD within 72 hours

## Never Log or Expose
- Passwords, tokens, API keys (even partial)
- NIF (tax ID), passport numbers in plain logs
- Full credit card numbers
- Private encryption keys

## API Security Checklist
- [ ] All endpoints require auth except verified public webhooks
- [ ] Rate limiting: 100 req/hour anonymous, 1000/hour authenticated per tenant
- [ ] Input validation via DRF serializers — never trust raw request.data
- [ ] CSRF protection enabled (Django default)
- [ ] CORS: whitelist specific origins, never allow *
- [ ] SQL: always use ORM — never raw SQL with user input
- [ ] File uploads: validate MIME type + size + scan for malware

## JWT Security
```python
# Short-lived access tokens
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=15),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,  # Requires token blacklist app
}
# Payload must include tenant_schema claim
```

## Audit Logging Pattern
```python
# Every write to critical models must be logged
AuditLog.objects.create(
    tenant=connection.tenant,
    user=request.user,
    action='UPDATE',
    model='Unit',
    object_id=str(unit.id),
    changes=changes_dict,
    ip_address=get_client_ip(request),
    timestamp=now()
)
```

## Sensitive Data in Models
```python
# Use django-cryptography for PII fields
from django_cryptography.fields import encrypt

class Buyer(models.Model):
    email = encrypt(models.EmailField())   # Encrypted at rest
    phone = encrypt(models.CharField())    # Encrypted at rest
    nif = encrypt(models.CharField())      # Encrypted at rest
    # But: name can be plaintext for search performance
```

## Security Scan in CI
```yaml
# .github/workflows/ci.yml
- name: Security scan
  run: |
    bandit -r apps/ -ll          # Python security linter
    safety check                  # Dependency vulnerabilities
    # OWASP ZAP scan on staging (weekly)
```

## OWASP Top 10 Mitigations
| Risk | Mitigation |
|------|-----------|
| A01 Broken Access Control | django-guardian RBAC + IsTenantMember on all views |
| A02 Cryptographic Failures | encrypt PII fields, HTTPS only, bcrypt passwords |
| A03 Injection | ORM always, serializer validation, parameterized queries |
| A05 Security Misconfiguration | .env files, DEBUG=False in prod, SECRET_KEY rotation |
| A07 Auth Failures | JWT blacklist, rate limit login, 2FA for admin |
| A09 Logging Failures | Structured logs, Sentry for errors, audit trail |
