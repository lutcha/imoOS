"""
Management command: populate_demo_data
Populates the demo_promotora tenant with realistic demo data for Cabo Verde.
Safe to run multiple times — uses get_or_create throughout.
"""
import uuid
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django_tenants.utils import tenant_context

from apps.tenants.models import Client


class Command(BaseCommand):
    help = 'Populates demo_promotora tenant with realistic demo data'

    def handle(self, *args, **options):
        try:
            tenant = Client.objects.get(schema_name='demo_promotora')
        except Client.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                'demo_promotora tenant not found. Run ensure_demo_tenant first.'
            ))
            return

        self.stdout.write(f'Populating tenant: {tenant.name} (schema: {tenant.schema_name})')
        with tenant_context(tenant):
            self._populate(tenant)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _populate(self, tenant):
        try:
            self._create_projects_and_inventory()
            self._create_crm_leads()
            self._create_contracts()
            self.stdout.write(self.style.SUCCESS('Demo data population complete.'))
        except Exception as exc:  # noqa: BLE001
            self.stderr.write(self.style.ERROR(f'Demo data population failed: {exc}'))
            raise

    # ------------------------------------------------------------------
    # Projects + Buildings + Floors + Units
    # ------------------------------------------------------------------

    def _create_projects_and_inventory(self):
        from apps.projects.models import Project, Building, Floor
        from apps.inventory.models import Unit, UnitType
        from apps.users.models import User

        admin = User.objects.filter(email='admin@demo.cv').first()

        # --- Unit types ---
        t1, _ = UnitType.objects.get_or_create(
            code='T1', defaults={'name': 'T1', 'bedrooms': 1, 'bathrooms': 1}
        )
        t2, _ = UnitType.objects.get_or_create(
            code='T2', defaults={'name': 'T2', 'bedrooms': 2, 'bathrooms': 1}
        )
        t3, _ = UnitType.objects.get_or_create(
            code='T3', defaults={'name': 'T3', 'bedrooms': 3, 'bathrooms': 2}
        )

        # --- Project 1 ---
        p1, created = Project.objects.get_or_create(
            slug='baia-das-gaivotas',
            defaults={
                'name': 'Empreendimento Baía das Gaivotas',
                'description': 'Condomínio residencial com vista para o mar na Baía de Palmarejo.',
                'status': Project.STATUS_CONSTRUCTION,
                'address': 'Palmarejo, Praia',
                'city': 'Praia',
                'island': 'Santiago',
                'start_date': date(2024, 3, 1),
                'expected_completion': date(2026, 12, 31),
                'created_by': admin,
            }
        )
        if created:
            self.stdout.write(f'  Created project: {p1.name}')

        # Buildings for project 1
        b1a, _ = Building.objects.get_or_create(
            project=p1, code='BG-A',
            defaults={'name': 'Bloco A', 'floors_count': 5}
        )
        b1b, _ = Building.objects.get_or_create(
            project=p1, code='BG-B',
            defaults={'name': 'Bloco B', 'floors_count': 5}
        )

        # --- Project 2 ---
        p2, created = Project.objects.get_or_create(
            slug='residencias-monte-verde',
            defaults={
                'name': 'Residências Monte Verde',
                'description': 'Moradias unifamiliares e apartamentos T2/T3 no Monte Verde.',
                'status': Project.STATUS_PLANNING,
                'address': 'Monte Verde, São Filipe',
                'city': 'São Filipe',
                'island': 'Fogo',
                'start_date': date(2025, 6, 1),
                'expected_completion': date(2027, 6, 30),
                'created_by': admin,
            }
        )
        if created:
            self.stdout.write(f'  Created project: {p2.name}')

        # Buildings for project 2
        b2a, _ = Building.objects.get_or_create(
            project=p2, code='MV-A',
            defaults={'name': 'Torre A', 'floors_count': 4}
        )
        b2b, _ = Building.objects.get_or_create(
            project=p2, code='MV-B',
            defaults={'name': 'Torre B', 'floors_count': 4}
        )

        # --- Floors (1 per building for demo) ---
        floor_b1a, _ = Floor.objects.get_or_create(building=b1a, number=1, defaults={'name': '1º Andar'})
        floor_b1b, _ = Floor.objects.get_or_create(building=b1b, number=1, defaults={'name': '1º Andar'})
        floor_b2a, _ = Floor.objects.get_or_create(building=b2a, number=1, defaults={'name': '1º Andar'})
        floor_b2b, _ = Floor.objects.get_or_create(building=b2b, number=1, defaults={'name': '1º Andar'})

        # --- Units (10 total, mix of types and statuses) ---
        units_spec = [
            # (floor, code, unit_type, status, area_bruta, price_cve)
            (floor_b1a, 'BG-A-P1-T2-01', t2, Unit.STATUS_SOLD,      85.0, Decimal('6500000')),
            (floor_b1a, 'BG-A-P1-T2-02', t2, Unit.STATUS_RESERVED,  88.0, Decimal('6800000')),
            (floor_b1a, 'BG-A-P1-T3-03', t3, Unit.STATUS_AVAILABLE, 110.0, Decimal('8500000')),
            (floor_b1b, 'BG-B-P1-T1-01', t1, Unit.STATUS_AVAILABLE,  55.0, Decimal('4200000')),
            (floor_b1b, 'BG-B-P1-T2-02', t2, Unit.STATUS_CONTRACT,   82.0, Decimal('6300000')),
            (floor_b2a, 'MV-A-P1-T2-01', t2, Unit.STATUS_AVAILABLE,  90.0, Decimal('7000000')),
            (floor_b2a, 'MV-A-P1-T3-02', t3, Unit.STATUS_AVAILABLE, 115.0, Decimal('9200000')),
            (floor_b2b, 'MV-B-P1-T1-01', t1, Unit.STATUS_AVAILABLE,  58.0, Decimal('4500000')),
            (floor_b2b, 'MV-B-P1-T2-02', t2, Unit.STATUS_SOLD,       86.0, Decimal('6600000')),
            (floor_b2b, 'MV-B-P1-T3-03', t3, Unit.STATUS_RESERVED,  112.0, Decimal('8900000')),
        ]

        self._unit_map = {}
        for floor, code, utype, ustatus, area, price in units_spec:
            unit, created = Unit.objects.get_or_create(
                floor=floor,
                code=code,
                defaults={
                    'unit_type': utype,
                    'status': ustatus,
                    'area_bruta': Decimal(str(area)),
                    'area_util': Decimal(str(round(area * 0.9, 2))),
                    'floor_number': floor.number,
                    'created_by': admin,
                }
            )
            self._unit_map[code] = unit
            if created:
                self.stdout.write(f'  Created unit: {unit.code} ({unit.get_status_display()})')

        self.stdout.write(f'  Units ready: {len(self._unit_map)}')

    # ------------------------------------------------------------------
    # CRM Leads
    # ------------------------------------------------------------------

    def _create_crm_leads(self):
        from apps.crm.models import Lead

        leads_data = [
            ('António', 'Évora',      'antonio.evora@gmail.com',      '+238 991 1234', Lead.STATUS_CONVERTED, Lead.STAGE_WON,           Lead.SOURCE_REFERRAL, 'T2'),
            ('Maria',   'Tavares',    'maria.tavares@outlook.com',     '+238 992 5678', Lead.STATUS_QUALIFIED,  Lead.STAGE_PROPOSAL_SENT, Lead.SOURCE_WEB,       'T3'),
            ('Carlos',  'Monteiro',   'cmonteiro@cvtelecom.cv',        '+238 993 4321', Lead.STATUS_NEW,        Lead.STAGE_NEW,           Lead.SOURCE_INSTAGRAM, 'T1'),
            ('Ana',     'Correia',    'ana.correia@imocv.cv',          '+238 994 8765', Lead.STATUS_CONVERTED,  Lead.STAGE_WON,           Lead.SOURCE_IMOCV,     'T2'),
            ('João',    'Fonseca',    'jfonseca@empresa.cv',           '+238 995 1111', Lead.STATUS_QUALIFIED,  Lead.STAGE_NEGOTIATION,   Lead.SOURCE_REFERRAL,  'T3'),
            ('Filipa',  'Delgado',    'filipa.delgado@gmail.com',      '+238 996 2222', Lead.STATUS_CONTACTED,  Lead.STAGE_CONTACTED,     Lead.SOURCE_FACEBOOK,  'T2'),
            ('Nelson',  'Rodrigues',  'nelson.rod@hotmail.com',        '+238 997 3333', Lead.STATUS_LOST,       Lead.STAGE_LOST,          Lead.SOURCE_WEB,       'T1'),
            ('Carla',   'Bettencourt','carla.b@yahoo.com',             '+238 998 4444', Lead.STATUS_QUALIFIED,  Lead.STAGE_VISIT_SCHEDULED, Lead.SOURCE_IMOCV,   'T2'),
        ]

        self._lead_map = {}
        for first, last, email, phone, lstatus, stage, source, typology in leads_data:
            lead, created = Lead.objects.get_or_create(
                email=email,
                defaults={
                    'first_name': first,
                    'last_name': last,
                    'phone': phone,
                    'status': lstatus,
                    'stage': stage,
                    'source': source,
                    'preferred_typology': typology,
                    'budget': Decimal('7000000'),
                    'notes': 'Lead criado pelo populate_demo_data.',
                }
            )
            self._lead_map[email] = lead
            if created:
                self.stdout.write(f'  Created lead: {lead.full_name}')

        self.stdout.write(f'  Leads ready: {len(self._lead_map)}')

    # ------------------------------------------------------------------
    # Contracts + Payments
    # ------------------------------------------------------------------

    def _create_contracts(self):
        from apps.contracts.models import Contract, Payment
        from apps.users.models import User

        admin = User.objects.filter(email='admin@demo.cv').first()

        contracts_spec = [
            # (lead_email, unit_code, contract_number, total_price_cve)
            ('antonio.evora@gmail.com', 'BG-A-P1-T2-01', 'DEMO-2026-001', Decimal('6500000')),
            ('ana.correia@imocv.cv',    'MV-B-P1-T2-02', 'DEMO-2026-002', Decimal('6600000')),
            ('joao.fonseca@empresa.cv', 'BG-B-P1-T2-02', 'DEMO-2026-003', Decimal('6300000')),
        ]

        # Patch missing email key
        joao_lead = None
        for lead in self._lead_map.values():
            if lead.first_name == 'João' and lead.last_name == 'Fonseca':
                joao_lead = lead
                break

        for lead_email, unit_code, contract_number, total_price in contracts_spec:
            lead = self._lead_map.get(lead_email)
            # João's email in our map is 'jfonseca@empresa.cv'
            if lead is None and lead_email == 'joao.fonseca@empresa.cv':
                lead = joao_lead
            if lead is None:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping contract {contract_number}: lead not found')
                )
                continue

            unit = self._unit_map.get(unit_code)
            if unit is None:
                self.stdout.write(
                    self.style.WARNING(f'  Skipping contract {contract_number}: unit not found')
                )
                continue

            contract, created = Contract.objects.get_or_create(
                contract_number=contract_number,
                defaults={
                    'unit': unit,
                    'lead': lead,
                    'vendor': admin,
                    'status': Contract.STATUS_ACTIVE,
                    'total_price_cve': total_price,
                    'signed_at': date.today() - timedelta(days=30),
                    'notes': 'Contrato de demonstração.',
                }
            )
            if created:
                self.stdout.write(f'  Created contract: {contract.contract_number}')

            # Payment plan: deposit + 3 instalments
            self._create_payment_plan(contract, total_price)

        self.stdout.write('  Contracts ready.')

    def _create_payment_plan(self, contract, total_price):
        from apps.contracts.models import Payment

        deposit_amount = (total_price * Decimal('0.20')).quantize(Decimal('0.01'))
        instalment_amount = (total_price * Decimal('0.25')).quantize(Decimal('0.01'))
        final_amount = total_price - deposit_amount - (instalment_amount * 3)

        base_date = date.today() - timedelta(days=30)

        payments_spec = [
            (Payment.PAYMENT_DEPOSIT,     deposit_amount,    base_date,                          Payment.STATUS_PAID),
            (Payment.PAYMENT_INSTALLMENT, instalment_amount, base_date + timedelta(days=30),     Payment.STATUS_PAID),
            (Payment.PAYMENT_INSTALLMENT, instalment_amount, base_date + timedelta(days=60),     Payment.STATUS_PENDING),
            (Payment.PAYMENT_INSTALLMENT, instalment_amount, base_date + timedelta(days=90),     Payment.STATUS_PENDING),
            (Payment.PAYMENT_FINAL,       final_amount,       base_date + timedelta(days=365),   Payment.STATUS_PENDING),
        ]

        for ptype, amount, due_date, pstatus in payments_spec:
            Payment.objects.get_or_create(
                contract=contract,
                payment_type=ptype,
                due_date=due_date,
                defaults={
                    'amount_cve': amount,
                    'status': pstatus,
                    'paid_date': due_date if pstatus == Payment.STATUS_PAID else None,
                }
            )
