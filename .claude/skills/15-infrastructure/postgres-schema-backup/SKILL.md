---
name: postgres-schema-backup
description: pg_dump por schema de inquilino, encriptação com GPG, upload para S3, procedimento de restauro, configuração de recuperação point-in-time e target Makefile.
argument-hint: "[tenant_slug]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Garantir backups individuais por schema de inquilino com encriptação em repouso. A recuperação point-in-time (PITR) via WAL archiving complementa os backups periódicos para casos de corrupção de dados.

## Code Pattern

```bash
#!/bin/bash
# scripts/backup_tenant_schema.sh

set -euo pipefail

TENANT_SLUG="${1:?Uso: $0 <tenant_slug>}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"
DB_NAME="${DB_NAME:-imoos}"
DB_USER="${DB_USER:-imoos}"
S3_BUCKET="${S3_BUCKET:-imoos-backups}"
GPG_KEY_ID="${GPG_KEY_ID:?Variável GPG_KEY_ID obrigatória}"

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="/tmp/backup_${TENANT_SLUG}_${TIMESTAMP}.sql"
ENCRYPTED_FILE="${BACKUP_FILE}.gpg"

echo "A fazer backup do schema '${TENANT_SLUG}'..."

# 1. Dump do schema específico
PGPASSWORD="${DB_PASSWORD}" pg_dump \
  -h "${DB_HOST}" \
  -p "${DB_PORT}" \
  -U "${DB_USER}" \
  -d "${DB_NAME}" \
  --schema="${TENANT_SLUG}" \
  --no-owner \
  --no-privileges \
  --format=custom \
  --file="${BACKUP_FILE}"

echo "Dump concluído: ${BACKUP_FILE} ($(du -sh ${BACKUP_FILE} | cut -f1))"

# 2. Encriptar com GPG
gpg --batch --yes \
  --encrypt \
  --recipient "${GPG_KEY_ID}" \
  --output "${ENCRYPTED_FILE}" \
  "${BACKUP_FILE}"

rm "${BACKUP_FILE}"
echo "Encriptado: ${ENCRYPTED_FILE}"

# 3. Upload para S3
S3_KEY="schemas/${TENANT_SLUG}/$(date +%Y/%m)/${TIMESTAMP}.sql.gpg"
aws s3 cp "${ENCRYPTED_FILE}" "s3://${S3_BUCKET}/${S3_KEY}" \
  --sse AES256 \
  --metadata "tenant=${TENANT_SLUG},timestamp=${TIMESTAMP}"

rm "${ENCRYPTED_FILE}"
echo "Backup enviado para s3://${S3_BUCKET}/${S3_KEY}"
```

```bash
# scripts/restore_tenant_schema.sh
#!/bin/bash
# Restaurar a partir de backup S3

TENANT_SLUG="${1:?}"
S3_KEY="${2:?}"

# Download e desencriptar
aws s3 cp "s3://${S3_BUCKET}/${S3_KEY}" /tmp/restore.sql.gpg
gpg --decrypt --output /tmp/restore.sql /tmp/restore.sql.gpg

# Restaurar no schema
psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
  -c "DROP SCHEMA IF EXISTS ${TENANT_SLUG} CASCADE;"
psql -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
  -c "CREATE SCHEMA ${TENANT_SLUG};"
PGPASSWORD="${DB_PASSWORD}" pg_restore \
  -h "${DB_HOST}" -U "${DB_USER}" -d "${DB_NAME}" \
  --schema="${TENANT_SLUG}" /tmp/restore.sql

echo "Schema '${TENANT_SLUG}' restaurado."
```

```makefile
# Makefile
.PHONY: backup-tenant restore-tenant backup-all

backup-tenant:
	@test -n "$(TENANT)" || (echo "Uso: make backup-tenant TENANT=<slug>" && exit 1)
	./scripts/backup_tenant_schema.sh $(TENANT)

backup-all:
	@for schema in $(shell psql -h $(DB_HOST) -U $(DB_USER) -d $(DB_NAME) -t -c \
	  "SELECT schema_name FROM information_schema.schemata WHERE schema_name NOT IN ('public','information_schema')"); do \
	  ./scripts/backup_tenant_schema.sh $$schema; \
	done

restore-tenant:
	@test -n "$(TENANT)" || (echo "Uso: make restore-tenant TENANT=<slug> S3_KEY=<key>" && exit 1)
	./scripts/restore_tenant_schema.sh $(TENANT) $(S3_KEY)
```

## Key Rules

- Encriptar SEMPRE com GPG antes do upload para S3 — proteção de dados em repouso.
- Agendar `backup-all` diariamente às 03:00 via cron ou GitHub Actions.
- Testar o restauro mensalmente para garantir que os backups são recuperáveis.
- Reter backups por 30 dias no S3 com `aws s3api put-bucket-lifecycle-configuration`.

## Anti-Pattern

```bash
# ERRADO: fazer dump de toda a base de dados sem encriptação
pg_dump imoos > backup.sql  # um dump da base completa mistura dados de todos os inquilinos
aws s3 cp backup.sql s3://bucket/  # sem encriptação — dados em texto claro no S3
```
