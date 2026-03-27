# ImoOS — Claude Project Context

## Produto
**ImoOS** — Sistema Operativo para Promotoras e Construtoras Imobiliárias
SaaS PropTech multi-tenant para Cabo Verde (expansão: Angola, Senegal)
Integração nativa com **imo.cv** (marketplace imobiliário)

## Stack Tecnológico
| Camada | Tech |
|--------|------|
| Backend | Python 3.11 + Django 4.2 + DRF |
| Tenancy | django-tenants (schema-per-tenant) |
| Frontend Web | Next.js 14 + TypeScript + Tailwind CSS |
| Mobile | React Native + TypeScript + WatermelonDB |
| Database | PostgreSQL 15 + PostGIS |
| Cache/Queue | Redis + Celery |
| Storage | S3-compatible (DigitalOcean Spaces) |
| Auth | JWT (djangorestframework-simplejwt) + django-guardian (RBAC) |
| Audit | django-simple-history em todos os modelos transacionais |

## Regras de Arquitetura (NAO NEGOCIAVEIS)

### Multi-Tenancy
- **Schema-per-tenant**: cada promotora tem o seu proprio schema PostgreSQL
- `SHARED_APPS`: apenas `tenants.Client`, `tenants.Domain`, auth infra
- `TENANT_APPS`: todos os modelos de negocio (projects, inventory, crm, etc.)
- **NUNCA** fazer queries cross-tenant sem `tenant_context()` explicito
- Celery tasks: sempre passar `tenant_id` como argumento, nunca objetos ORM

### Segurança
- Todos os endpoints requerem autenticacao exceto webhooks publicos verificados
- Rate limiting em todos os endpoints publicos: 100 req/hora por IP
- Secrets NUNCA no codigo — apenas em environment variables
- HTTPS obrigatorio em producao
- Audit logs imutaveis para todas as operacoes criticas

### Qualidade
- Coverage minimo 80% nas apps core (tenants, projects, inventory, crm)
- Testes de isolamento de tenant OBRIGATORIOS antes de qualquer merge
- CI pipeline deve passar antes de merge (lint + test + security scan)
- PR review time target: <24 horas

### Dados
- UUIDs como primary keys em todos os modelos de negocio
- `created_at` e `updated_at` em todos os modelos
- `simple_history` em: Project, Unit, Contract, Payment, Reservation
- GeoJSON/PostGIS para localizacao de projetos e terrenos
- S3 prefixo por tenant: `tenants/{tenant_slug}/...`

## Estrutura do Repositorio
```
apps/           # Django apps (core, tenants, projects, inventory, crm, ...)
config/         # Settings modulares (base, development, staging, production)
tests/          # Suite de testes (unit, integration, tenant_isolation)
docker/         # Dockerfiles
frontend/       # Next.js app
mobile/         # React Native app
requirements/   # Python dependencies por ambiente
.github/        # CI/CD workflows
.claude/skills/ # Claude Skills para desenvolvimento
```

## Contexto Cabo Verde
- Moeda primaria: CVE (Escudo Cabo-Verdiano), secundaria: EUR
- Lingua: pt-PT (preparar para pt-AO, fr-SN)
- Timezone: Atlantic/Cape_Verde (UTC-1)
- Compliance: Lei n.o 133/V/2019 (protecao de dados)
- Conectividade: design offline-first para app de obra
- Pagamentos: MBE (Multibanco), transferencia bancaria
- WhatsApp > email para comunicacao comercial

## Skills Disponiveis
Consultar `.claude/skills/` para 105 skills organizados por dominio:
- `00-global`: contexto, padroes, segurança, i18n
- `01-multi-tenant`: padroes django-tenants
- `02-backend-django`: DRF viewsets, serializers, filtros
- `03-async-celery`: tasks assincronas tenant-safe
- `04-frontend-nextjs`: routing, auth, React Query
- `05-16`: modulos de negocio (tenants, projects, inventory, crm, contracts, construction, marketplace, investors, cms)
- `14-testing`: fixtures, isolamento, E2E, load tests
- `15-infrastructure`: Docker, CI/CD, monitoring
- `16-security-compliance`: LGPD, audit, JWT, pentest

## Comandos Frequentes
```bash
# Desenvolvimento local
docker-compose -f docker-compose.dev.yml up

# Migrations
python manage.py migrate_schemas --shared   # Schema publico
python manage.py migrate_schemas             # Todos os tenants

# Criar tenant
python manage.py create_tenant --schema=empresa_a --name="Empresa A" --domain=empresa-a.imos.cv

# Testes
pytest tests/tenant_isolation/              # Critico — corre sempre
pytest --cov=apps --cov-report=term-missing # Coverage report
make test                                   # Suite completa via Makefile

# CI/CD
make lint                                   # flake8 + black + isort
make security                               # bandit + safety
```

## Definicao de Pronto (DoD)
- [ ] Codigo implementado seguindo padroes (black, flake8, type hints)
- [ ] Testes unitarios escritos e passando (coverage >= 80%)
- [ ] Testes de isolamento de tenant passando
- [ ] Code review aprovado pelo Tech Lead
- [ ] Deploy em staging validado
- [ ] Documentacao da API atualizada (drf-spectacular)
