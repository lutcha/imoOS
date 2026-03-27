from decimal import Decimal
import random
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.gis.geos import Point
from django_tenants.utils import tenant_context
from faker import Faker

from apps.tenants.models import Client
from apps.projects.models import Project, Building, Floor
from apps.inventory.models import UnitType, Unit, UnitPricing
from apps.crm.models import Lead, UnitReservation
from apps.contracts.models import Contract, Payment
from apps.marketplace.models import MarketplaceListing, ImoCvWebhookLog

class Command(BaseCommand):
    help = 'Seed demo data for a specific tenant'

    def add_arguments(self, parser):
        parser.add_argument('--tenant', type=str, required=True, help='Tenant schema name')

    def handle(self, *args, **options):
        schema_name = options['tenant']
        try:
            tenant = Client.objects.get(schema_name=schema_name)
        except Client.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Tenant "{schema_name}" does not exist.'))
            return

        fake = Faker(['pt_PT'])

        with tenant_context(tenant):
            self.stdout.write(self.style.SUCCESS(f'Seeding data for tenant: {tenant.name}'))

            # 1. Project
            project, created = Project.objects.get_or_create(
                slug='residencial-atlantico',
                defaults={
                    'name': 'Residencial Atlântico',
                    'description': 'Empreendimento de luxo frente ao mar na Prainha.',
                    'status': Project.STATUS_CONSTRUCTION,
                    'city': 'Praia',
                    'island': 'Santiago',
                    'location': Point(-23.5092, 14.9177),
                    'start_date': timezone.now().date() - timezone.timedelta(days=180),
                    'expected_completion': timezone.now().date() + timezone.timedelta(days=365),
                }
            )
            if created:
                self.stdout.write(f'Created project: {project.name}')

            # 2. Building
            building, created = Building.objects.get_or_create(
                project=project,
                code='BLOCO-A',
                defaults={
                    'name': 'Bloco A',
                    'floors_count': 5
                }
            )

            # 3. Floors
            for i in range(5):
                Floor.objects.get_or_create(
                    building=building,
                    number=i,
                    defaults={'name': f'Piso {i}' if i > 0 else 'Rés-do-Chão'}
                )

            # 4. Unit Types
            t2, _ = UnitType.objects.get_or_create(name='T2', code='T2', defaults={'bedrooms': 2, 'bathrooms': 1})
            t3, _ = UnitType.objects.get_or_create(name='T3', code='T3', defaults={'bedrooms': 3, 'bathrooms': 2})
            loja, _ = UnitType.objects.get_or_create(name='Loja', code='L', defaults={'bedrooms': 0, 'bathrooms': 1})

            # 5. Units & Pricing
            units_data = [
                ('A-0-L1', loja, 0, 80.00, 15000000, Unit.STATUS_AVAILABLE),
                ('A-1-101', t2, 1, 75.50, 8500000, Unit.STATUS_AVAILABLE),
                ('A-1-102', t2, 1, 75.50, 8500000, Unit.STATUS_RESERVED),
                ('A-2-201', t3, 2, 110.00, 12500000, Unit.STATUS_CONTRACT),
                ('A-2-202', t3, 2, 110.00, 12500000, Unit.STATUS_AVAILABLE),
                ('A-3-301', t2, 3, 75.50, 9000000, Unit.STATUS_AVAILABLE),
                ('A-4-PH', t3, 4, 150.00, 22000000, Unit.STATUS_AVAILABLE),
            ]

            for code, utype, fnum, area, price, status in units_data:
                floor = Floor.objects.get(building=building, number=fnum)
                unit, created = Unit.objects.get_or_create(
                    floor=floor,
                    code=code,
                    defaults={
                        'unit_type': utype,
                        'area_bruta': Decimal(str(area)),
                        'status': status,
                        'floor_number': fnum
                    }
                )
                if created:
                    UnitPricing.objects.get_or_create(
                        unit=unit,
                        defaults={
                            'price_cve': Decimal(str(price)),
                            'price_eur': Decimal(str(price)) / Decimal('110.265')
                        }
                    )
                
                # 6. Marketplace Listings (idempotent)
                if code in ['A-1-101', 'A-3-301']:
                    MarketplaceListing.objects.get_or_create(
                        unit=unit,
                        defaults={
                            'imocv_listing_id': f'IMOCV-{random.randint(1000, 9999)}',
                            'status': MarketplaceListing.STATUS_PUBLISHED,
                            'published_at': timezone.now() - timezone.timedelta(days=random.randint(1, 30))
                        }
                    )

            # 7. Leads
            lead_emails = [
                'joao.silva@demo.imos.cv', 'maria.santos@demo.imos.cv', 'antonio.gomes@demo.imos.cv',
                'ana.pereira@demo.imos.cv', 'carlos.rod@demo.imos.cv', 'lisa.vaz@demo.imos.cv'
            ]
            lead_sources = [Lead.SOURCE_IMOCV, Lead.SOURCE_WEB, Lead.SOURCE_INSTAGRAM, Lead.SOURCE_FACEBOOK]
            for email in lead_emails:
                l, created = Lead.objects.get_or_create(
                    email=email,
                    defaults={
                        'first_name': fake.first_name(),
                        'last_name': fake.last_name(),
                        'phone': f'+2389{random.randint(100000, 999999)}',
                        'source': random.choice(lead_sources),
                        'status': random.choice([Lead.STATUS_NEW, Lead.STATUS_CONTACTED, Lead.STATUS_QUALIFIED]),
                        'stage': random.choice([Lead.STAGE_NEW, Lead.STAGE_CONTACTED, Lead.STAGE_VISIT_SCHEDULED]),
                        'budget': Decimal(str(random.randint(5000000, 20000000)))
                    }
                )
                
                # Mockup some webhook logs for one lead
                if email == 'joao.silva@demo.imos.cv':
                    ImoCvWebhookLog.objects.get_or_create(
                        event_type=ImoCvWebhookLog.EVENT_LEAD_CAPTURED,
                        imocv_listing_id='IMOCV-DEMO-001',
                        defaults={
                            'payload': {'first_name': l.first_name, 'last_name': l.last_name, 'email': l.email},
                            'processed_at': timezone.now()
                        }
                    )

            # 8. Reservations & Contracts
            try:
                reserved_unit = Unit.objects.get(code='A-1-102')
                lead = Lead.objects.get(email='maria.santos@demo.imos.cv')
                UnitReservation.objects.get_or_create(
                    unit=reserved_unit,
                    defaults={
                        'lead': lead,
                        'status': UnitReservation.STATUS_ACTIVE,
                        'expires_at': timezone.now() + timezone.timedelta(days=2),
                        'deposit_amount_cve': Decimal('100000.00')
                    }
                )
            except Unit.DoesNotExist:
                pass

            try:
                contract_unit = Unit.objects.get(code='A-2-201')
                lead_contract = Lead.objects.get(email='antonio.gomes@demo.imos.cv')
                contract, created = Contract.objects.get_or_create(
                    unit=contract_unit,
                    defaults={
                        'lead': lead_contract,
                        'contract_number': f'OS-{timezone.now().year}-001',
                        'status': Contract.STATUS_ACTIVE,
                        'total_price_cve': contract_unit.pricing.price_cve,
                        'signed_at': timezone.now() - timezone.timedelta(days=5)
                    }
                )
                if created:
                    Payment.objects.get_or_create(
                        contract=contract,
                        payment_type=Payment.PAYMENT_DEPOSIT,
                        defaults={
                            'amount_cve': Decimal('500000.00'),
                            'due_date': timezone.now().date() - timezone.timedelta(days=10),
                            'status': Payment.STATUS_PAID,
                            'paid_date': timezone.now().date() - timezone.timedelta(days=10)
                        }
                    )
                    Payment.objects.get_or_create(
                        contract=contract,
                        payment_type=Payment.PAYMENT_INSTALLMENT,
                        due_date=timezone.now().date() + timezone.timedelta(days=30),
                        defaults={
                            'amount_cve': Decimal('1000000.00'),
                            'status': Payment.STATUS_PENDING
                        }
                    )
            except Unit.DoesNotExist:
                pass

            self.stdout.write(self.style.SUCCESS('Demo data seeded successfully!'))
