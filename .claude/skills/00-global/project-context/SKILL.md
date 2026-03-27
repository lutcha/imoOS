---
name: project-context
description: Provide ImoOS project overview, architecture rules, and Cabo Verde context for all code generation
argument-hint: [module] [task]
allowed-tools: Read, Grep
---

# ImoOS Project Context

## Overview
ImoOS is a multi-tenant PropTech SaaS for Cabo Verde real estate developers.
- Backend: Django 4.2 + django-tenants (schema-per-tenant)
- Frontend: Next.js 14 + TypeScript + Tailwind
- Database: PostgreSQL 15 (one schema per tenant)
- Queue: Celery + Redis
- Auth: JWT with tenant claims

## Critical Architecture Rules
1. ALL business models live in TENANT_APPS → isolated per schema
2. SHARED_APPS only for: tenants.Client, tenants.Domain, auth infra
3. NEVER query across tenant schemas — use tenant_context() always
4. Celery tasks: pass tenant_id, re-fetch tenant, wrap in tenant_context()
5. API permissions: IsTenantMember checks JWT tenant_schema vs active schema

## Cabo Verde Specifics
- Currency: CVE (primary), EUR (secondary for investors)
- Language: pt-PT (European Portuguese), prepare for pt-AO, fr-SN
- Timezone: Atlantic/Cape_Verde (UTC-1)
- Compliance: Lei n.º 133/V/2019 (data protection)
- Connectivity: Design for intermittent internet (offline-first mobile)

## When Generating Code
- Always include tenant isolation in models/views/tests
- Use django-tenants utilities: tenant_context, schema_context
- Prefix S3 uploads with tenant slug: tenants/{slug}/...
- Log usage/audit per tenant (no cross-tenant aggregation unless explicit)
- Optimize for mobile: large touch targets, minimal data usage
