"""
create_pilot_tenant — ImoOS management command

Creates a pilot tenant with realistic demo data for the Cabo Verde go-live.
Extends the existing create_tenant patterns with demo projects, units, and leads.

Usage:
  python manage.py create_pilot_tenant \\
    --schema=tecnicil \\
    --name="Tecnicil Imobiliário" \\
    --domain=tecnicil.imos.cv \\
    --city=Praia \\
    --island=Santiago \\
    --plan=pro \\
    --with-demo-data

Pilot promotoras:
  python manage.py create_pilot_tenant --schema=tecnicil --name="Tecnicil Imobiliário" \\
    --domain=tecnicil.imos.cv --city=Praia --plan=pro --with-demo-data
  python manage.py create_pilot_tenant --schema=mar_azul --name="Imobiliária Mar Azul" \\
    --domain=marazul.imos.cv --city=Mindelo --island="São Vicente" --plan=starter --with-demo-data
  python manage.py create_pilot_tenant --schema=construcoes_fogo --name="Construções Fogo" \\
    --domain=fogoimobiliaria.imos.cv --city="São Filipe" --island=Fogo --plan=starter --with-demo-data
"""
import re
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django_tenants.utils import tenant_context


class Command(BaseCommand):
    help = 'Cria tenant piloto Cabo Verde com dados demo realistas'

    def add_arguments(self, parser):
        parser.add_argument('--schema', required=True,
                            help='PostgreSQL schema name (lowercase, underscores only)')
        parser.add_argument('--name', required=True,
                            help='Company display name')
        parser.add_argument('--domain', required=True,
                            help='Primary domain (e.g. tecnicil.imos.cv)')
        parser.add_argument('--city', default='Praia',
                            help='City name used in demo project data')
        parser.add_argument('--island', default='Santiago',
                            help='Island name (e.g. Santiago, São Vicente, Fogo)')
        parser.add_argument('--plan', default='starter',
                            choices=['starter', 'pro', 'enterprise'])
        parser.add_argument('--with-demo-data', action='store_true',
                            help='Seed demo projects, units, and leads')

    def handle(self, *args, **options):  # noqa: C901
        from apps.memberships.models import TenantMembership
        from apps.tenants.models import Client, Domain, TenantSettings

        schema = options['schema']
        name = options['name']
        domain_name = options['domain']
        slug = schema.replace('_', '-')
        plan = options['plan']

        # ------------------------------------------------------------------
        # Pre-flight
        # ------------------------------------------------------------------
        if not re.match(r'^[a-z][a-z0-9_]*$', schema):
            raise CommandError(
                'schema deve ser lowercase, apenas letras/dígitos/underscores, '
                'começando com letra.'
            )
        if Client.objects.filter(schema_name=schema).exists():
            raise CommandError(f"Tenant '{schema}' já existe.")
        if Client.objects.filter(slug=slug).exists():
            raise CommandError(f"Slug '{slug}' já em uso.")
        if Domain.objects.filter(domain=domain_name).exists():
            raise CommandError(f"Domínio '{domain_name}' já registado.")

        self.stdout.write(f"A criar tenant '{name}' …")
        self.stdout.write(f"  schema : {schema}")
        self.stdout.write(f"  domain : {domain_name}")
        self.stdout.write(f"  plan   : {plan}")

        # ------------------------------------------------------------------
        # 1. Tenant (auto-migrates schema on save)
        # ------------------------------------------------------------------
        try:
            client = Client(
                schema_name=schema,
                name=name,
                slug=slug,
                plan=plan,
                country='CV',
                currency='CVE',
                is_active=True,
            )
            client.save()
        except Exception as exc:
            raise CommandError(f'Falha ao criar tenant: {exc}') from exc

        self.stdout.write(self.style.SUCCESS(
            f"  Schema '{schema}' criado e migrations aplicadas."
        ))

        # ------------------------------------------------------------------
        # 2. Domain
        # ------------------------------------------------------------------
        Domain.objects.create(domain=domain_name, tenant=client, is_primary=True)
        self.stdout.write(f"  Domínio '{domain_name}' registado.")

        # ------------------------------------------------------------------
        # 3. TenantSettings (public schema — plan limits only)
        # ------------------------------------------------------------------
        plan_limits = {
            'starter':    {'max_projects': 3,   'max_units': 150,  'max_users': 10},
            'pro':        {'max_projects': 20,  'max_units': 1000, 'max_users': 50},
            'enterprise': {'max_projects': 0,   'max_units': 0,    'max_users': 0},
        }
        limits = plan_limits[plan]
        TenantSettings.objects.create(
            tenant=client,
            max_projects=limits['max_projects'],
            max_units=limits['max_units'],
            max_users=limits['max_users'],
        )

        # ------------------------------------------------------------------
        # 4. Admin user + demo data (inside tenant schema)
        # ------------------------------------------------------------------
        with tenant_context(client):
            User = get_user_model()
            admin_email = f"admin@{slug}.cv"
            admin = User.objects.create_user(
                email=admin_email,
                password='ImoOS2026!',
                first_name='Admin',
                last_name=name.split()[0],
                is_staff=False,
            )
            TenantMembership.objects.create(
                user=admin,
                role=TenantMembership.ROLE_ADMIN,
                is_active=True,
            )
            self.stdout.write(f"  Admin '{admin_email}' criado.")

            if options['with_demo_data']:
                self._create_demo_data(slug, options)

        # ------------------------------------------------------------------
        # Summary
        # ------------------------------------------------------------------
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f"✅ {name} pronto."))
        self.stdout.write(f"  Login : {admin_email} / ImoOS2026!")
        self.stdout.write(f"  URL   : https://{domain_name}")

    def _create_demo_data(self, slug: str, options: dict) -> None:
        """
        Seed one project (Torre A, 6 units across 2 floors) + 3 Cape Verdean leads.
        Must be called inside tenant_context(client).
        """
        from apps.crm.models import Lead
        from apps.inventory.models import Unit, UnitPricing, UnitType
        from apps.projects.models import Building, Floor, Project

        city = options['city']
        island = options.get('island', 'Santiago')

        # Project
        project = Project.objects.create(
            name=f"Residencial {city} Norte",
            slug=f"{slug}-norte",
            description=(
                f"Complexo residencial moderno no norte de {city}, Cabo Verde. "
                "Apartamentos T1, T2 e T3 com acabamentos de qualidade."
            ),
            status=Project.STATUS_CONSTRUCTION,
            city=city,
            island=island,
            address=f"Achada Santo António, {city}",
        )
        building = Building.objects.create(
            project=project,
            name='Torre A',
            code='TORRE-A',
            floors_count=8,
        )
        self.stdout.write(f"  Projecto '{project.name}' criado.")

        # UnitTypes (get_or_create — idempotent within schema)
        t1, _ = UnitType.objects.get_or_create(
            code='T1', defaults={'name': 'T1', 'bedrooms': 1, 'bathrooms': 1}
        )
        t2, _ = UnitType.objects.get_or_create(
            code='T2', defaults={'name': 'T2', 'bedrooms': 2, 'bathrooms': 1}
        )
        t3, _ = UnitType.objects.get_or_create(
            code='T3', defaults={'name': 'T3', 'bedrooms': 3, 'bathrooms': 2}
        )

        # Units: (code, unit_type, floor_number, area_bruta_m2, price_cve, status)
        # Prices in CVE — realistic range for Cabo Verde (4.8M–9M CVE)
        unit_specs = [
            ('A-P0-01', t2, 0, Decimal('75.00'),  6_500_000, Unit.STATUS_AVAILABLE),
            ('A-P0-02', t3, 0, Decimal('95.00'),  8_200_000, Unit.STATUS_RESERVED),
            ('A-P0-03', t2, 0, Decimal('75.00'),  6_500_000, Unit.STATUS_AVAILABLE),
            ('A-P1-01', t1, 1, Decimal('55.00'),  4_800_000, Unit.STATUS_AVAILABLE),
            ('A-P1-02', t3, 1, Decimal('100.00'), 9_000_000, Unit.STATUS_SOLD),
            ('A-P1-03', t2, 1, Decimal('80.00'),  7_100_000, Unit.STATUS_AVAILABLE),
        ]
        CVE_EUR_RATE = Decimal('110.265')

        for code, utype, floor_num, area, price_cve_int, status in unit_specs:
            floor, _ = Floor.objects.get_or_create(
                building=building, number=floor_num,
                defaults={'name': 'Rés-do-Chão' if floor_num == 0 else f'{floor_num}º Andar'},
            )
            unit = Unit.objects.create(
                floor=floor,
                unit_type=utype,
                code=code,
                area_bruta=area,
                floor_number=floor_num,
                status=status,
            )
            price_cve = Decimal(str(price_cve_int))
            UnitPricing.objects.create(
                unit=unit,
                price_cve=price_cve,
                price_eur=(price_cve / CVE_EUR_RATE).quantize(Decimal('0.01')),
            )

        self.stdout.write(f"  {len(unit_specs)} unidades + UnitPricing criados.")

        # Leads — names typical of Cabo Verde / Lusophone Africa
        leads_data = [
            ('João',   'Tavares', 'joao.tavares@gmail.com',  '+238 991 2345', Lead.STAGE_VISIT_SCHEDULED),
            ('Maria',  'Silva',   'msilva@cvtelecom.cv',     '+238 992 8765', Lead.STAGE_CONTACTED),
            ('Carlos', 'Santos',  'csantos@yahoo.com',       '+238 993 4521', Lead.STAGE_NEW),
        ]
        for first, last, email, phone, stage in leads_data:
            Lead.objects.create(
                first_name=first,
                last_name=last,
                email=email,
                phone=phone,
                source=Lead.SOURCE_WEB,
                stage=stage,
                budget=Decimal('7000000.00'),  # ~7M CVE typical budget
            )
        self.stdout.write(f"  {len(leads_data)} leads criados.")
