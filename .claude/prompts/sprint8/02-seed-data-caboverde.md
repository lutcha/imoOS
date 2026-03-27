# Sprint 8 — Seed Data: Promotoras Piloto Cabo Verde

## Contexto

Para o go-live precisamos de dados reais de 2-3 promotoras piloto em Cabo Verde.
Este prompt cria:
1. Management command `create_pilot_tenant` para cada promotora
2. Dados demo realistas (projectos, unidades, leads) com contexto CVE/pt-PT
3. Fixtures para ambiente de staging

Promotoras piloto alvo:
- **Tecnicil Imobiliário** (Praia, Santiago) — maior promotora CV
- **Imobiliária Mar Azul** (Mindelo, São Vicente) — especialista em litoral
- **Construções Fogo** (São Filipe, Fogo) — mercado regional

## Pré-requisitos — Ler antes de começar

```
apps/tenants/management/         → management commands existentes
apps/tenants/models.py           → Client, TenantSettings, Domain
apps/projects/models.py          → Project, Building
apps/inventory/models.py         → Unit (status, tipologia, preço CVE)
apps/crm/models.py               → Lead, PipelineStage
```

```bash
ls apps/tenants/management/commands/
python manage.py --help | grep tenant
```

## Skills a carregar

```
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/05-module-tenants/tenant-lifecycle/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `django-tenants-specialist` | Management command `create_pilot_tenant` |
| `model-architect` | Fixtures com dados realistas CVE |

---

## Tarefa 1 — Management command: create_pilot_tenant

Criar `apps/tenants/management/commands/create_pilot_tenant.py`:

```python
"""
Cria um tenant piloto com dados demo realistas para Cabo Verde.

Uso:
  python manage.py create_pilot_tenant \
    --schema=tecnicil \
    --name="Tecnicil Imobiliário" \
    --domain=tecnicil.imos.cv \
    --city=Praia \
    --phone="+238 261 5000" \
    --email=info@tecnicil.cv \
    --plan=pro \
    --with-demo-data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django_tenants.utils import tenant_context


class Command(BaseCommand):
    help = 'Cria tenant piloto Cabo Verde com dados demo'

    def add_arguments(self, parser):
        parser.add_argument('--schema',   required=True)
        parser.add_argument('--name',     required=True)
        parser.add_argument('--domain',   required=True)
        parser.add_argument('--city',     default='Praia')
        parser.add_argument('--phone',    default='')
        parser.add_argument('--email',    default='')
        parser.add_argument('--plan',     default='starter', choices=['starter', 'pro', 'enterprise'])
        parser.add_argument('--with-demo-data', action='store_true')

    def handle(self, *args, **options):
        from apps.tenants.models import Client, Domain, TenantSettings
        from apps.memberships.models import TenantMembership

        # 1. Criar tenant
        tenant = Client(
            schema_name=options['schema'],
            name=options['name'],
            plan=options['plan'],
            status='ACTIVE',
        )
        tenant.save()

        # 2. Criar domain
        Domain.objects.create(
            domain=options['domain'],
            tenant=tenant,
            is_primary=True,
        )
        # Alias localhost para desenvolvimento local
        if options['schema'] == 'demo_promotora':
            Domain.objects.create(
                domain='demo.localhost',
                tenant=tenant,
                is_primary=False,
            )

        self.stdout.write(self.style.SUCCESS(f"Tenant criado: {tenant.schema_name}"))

        with tenant_context(tenant):
            User = get_user_model()

            # 3. Criar super-admin do tenant
            admin = User.objects.create_user(
                email=f"admin@{options['schema'].replace('_', '-')}.cv",
                password='ImoOS2026!',
                first_name='Admin',
                last_name=options['name'].split()[0],
                is_staff=False,
            )
            TenantMembership.objects.create(
                user=admin,
                role=TenantMembership.ROLE_ADMIN,
                is_active=True,
            )

            # 4. TenantSettings
            TenantSettings.objects.update_or_create(
                tenant=tenant,
                defaults={
                    'company_name': options['name'],
                    'city': options['city'],
                    'phone': options['phone'],
                    'email': options.get('email', ''),
                    'currency': 'CVE',
                    'timezone': 'Atlantic/Cape_Verde',
                },
            )

            # 5. Dados demo
            if options['with_demo_data']:
                self._create_demo_data(tenant, options)

        self.stdout.write(self.style.SUCCESS(f"✅ {options['name']} criado com sucesso"))

    def _create_demo_data(self, tenant, options):
        from apps.projects.models import Project, Building
        from apps.inventory.models import Unit

        city = options['city']

        # Projecto 1
        project = Project.objects.create(
            name=f"Residencial {city} Norte",
            description=f"Complexo residencial moderno no norte de {city}, Cabo Verde.",
            status='CONSTRUCTION',
            city=city,
            address=f"Achada Santo António, {city}",
        )
        building = Building.objects.create(
            project=project,
            name='Torre A',
            code='TORRE-A',
            floors_count=8,
        )

        # Unidades T1, T2, T3 com preços CVE realistas
        units_data = [
            ('A101', 'T2', 75, 6_500_000, 'AVAILABLE'),
            ('A102', 'T3', 95, 8_200_000, 'RESERVED'),
            ('A103', 'T2', 75, 6_500_000, 'AVAILABLE'),
            ('A201', 'T1', 55, 4_800_000, 'AVAILABLE'),
            ('A202', 'T3', 100, 9_000_000, 'SOLD'),
            ('A203', 'T2', 80, 7_100_000, 'AVAILABLE'),
        ]
        for code, typology, area, price_cve, status in units_data:
            Unit.objects.create(
                building=building,
                code=code,
                typology=typology,
                gross_area=area,
                price_cve=price_cve,
                price_eur=int(price_cve / 110.265),  # taxa CVE/EUR fixa
                floor=int(code[1]) - 1,
                status=status,
            )

        self.stdout.write(f"  📦 {len(units_data)} unidades criadas")
```

---

## Tarefa 2 — Criação das 3 promotoras piloto

```bash
# Promotora 1: Tecnicil (Praia, plano Pro)
python manage.py create_pilot_tenant \
  --schema=tecnicil \
  --name="Tecnicil Imobiliário" \
  --domain=tecnicil.imos.cv \
  --city=Praia \
  --plan=pro \
  --with-demo-data

# Promotora 2: Mar Azul (Mindelo, plano Starter)
python manage.py create_pilot_tenant \
  --schema=mar_azul \
  --name="Imobiliária Mar Azul" \
  --domain=marazul.imos.cv \
  --city=Mindelo \
  --plan=starter \
  --with-demo-data

# Promotora 3: Construções Fogo (São Filipe, plano Starter)
python manage.py create_pilot_tenant \
  --schema=construcoes_fogo \
  --name="Construções Fogo" \
  --domain=fogoimobiliaria.imos.cv \
  --city="São Filipe" \
  --plan=starter \
  --with-demo-data
```

---

## Tarefa 3 — Fixtures de staging

```bash
# Exportar dados demo para fixtures reutilizáveis
python manage.py dumpdata \
  tenants.client tenants.domain tenants.tenantsettings \
  --indent 2 > fixtures/staging_tenants.json

# Importar em staging
python manage.py loaddata fixtures/staging_tenants.json
python manage.py migrate_schemas
```

---

## Tarefa 4 — Seed de leads CVE

Dentro de cada tenant, criar leads com nomes e contactos típicos de Cabo Verde:

```python
# Em create_demo_data, adicionar:
from apps.crm.models import Lead

leads_data = [
    ('João Tavares', 'joao.tavares@gmail.com', '+238 991 2345', 'VISITED'),
    ('Maria Silva', 'msilva@cvtelecom.cv', '+238 992 8765', 'CONTACTED'),
    ('Carlos Santos', 'csantos@yahoo.com', '+238 993 4521', 'NEW'),
]
for name, email, phone, stage in leads_data:
    first, *rest = name.split()
    Lead.objects.create(
        first_name=first,
        last_name=' '.join(rest),
        email=email,
        phone=phone,
        pipeline_stage=stage,
        source='WEBSITE',
        budget_cve=7_000_000,
    )
```

## Verificação final

- [ ] 3 schemas criados: `tecnicil`, `mar_azul`, `construcoes_fogo`
- [ ] Login `admin@tecnicil.cv` / `ImoOS2026!` funciona em `tecnicil.imos.cv`
- [ ] Cada tenant tem 1 projecto + 6 unidades + 3 leads
- [ ] Preços em CVE (5-9 milhões) — valores realistas para Cabo Verde
- [ ] Tenant isolation: `admin@tecnicil.cv` NÃO vê dados de `mar_azul`
- [ ] `pytest tests/tenant_isolation/` → 100% passing com 3 tenants
