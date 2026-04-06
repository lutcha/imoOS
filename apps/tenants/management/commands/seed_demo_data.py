"""
Management command to seed demo tenant with realistic data.
Usage: python manage.py seed_demo_data [--tenant=demo_promotora]
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone
from datetime import datetime, timedelta
import random

from apps.tenants.models import Tenant


class Command(BaseCommand):
    help = 'Seed demo tenant with realistic construction project data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--tenant',
            type=str,
            default='demo_promotora',
            help='Schema name of the tenant to seed'
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing data before seeding'
        )

    def handle(self, *args, **options):
        schema_name = options['tenant']
        reset = options['reset']

        # Check if tenant exists
        try:
            tenant = Tenant.objects.get(schema_name=schema_name)
        except Tenant.DoesNotExist:
            raise CommandError(f'Tenant {schema_name} does not exist. Run create_demo_tenant first.')

        self.stdout.write(self.style.NOTICE(f'Seeding data for tenant: {tenant.name}'))

        # Switch to tenant schema
        connection.set_tenant(tenant)

        with transaction.atomic():
            if reset:
                self.clear_existing_data()
            
            # Create data in sequence
            users = self.create_users()
            leads = self.create_leads(users)
            projects = self.create_projects()
            units = self.create_units(projects)
            contracts = self.create_contracts(leads, units, users)
            construction_projects = self.create_construction_projects(contracts, users)
            self.create_phases_and_tasks(construction_projects, users)
            self.create_budgets(construction_projects)
            self.create_daily_reports(construction_projects, users)
            
        self.stdout.write(self.style.SUCCESS(f'\n✅ Demo data seeded successfully for {tenant.name}!'))
        self.print_summary()

    def clear_existing_data(self):
        """Clear existing demo data"""
        from apps.construction.models import DailyReport, ConstructionTask, ConstructionPhase, ConstructionProject
        from apps.contracts.models import Contract
        from apps.crm.models import Lead
        from apps.projects.models import Unit, Project
        
        self.stdout.write('Clearing existing data...')
        DailyReport.objects.all().delete()
        ConstructionTask.objects.all().delete()
        ConstructionPhase.objects.all().delete()
        ConstructionProject.objects.all().delete()
        Contract.objects.all().delete()
        Lead.objects.all().delete()
        Unit.objects.all().delete()
        Project.objects.all().delete()

    def create_users(self):
        """Create demo users with different roles"""
        from apps.users.models import User
        
        self.stdout.write('Creating users...')
        
        users_data = [
            {'email': 'admin@demo.cv', 'first_name': 'Carlos', 'last_name': 'Fonseca', 'role': 'ADMIN', 'is_staff': True},
            {'email': 'gerente@demo.cv', 'first_name': 'Maria', 'last_name': 'Silva', 'role': 'MANAGER'},
            {'email': 'vendas@demo.cv', 'first_name': 'João', 'last_name': 'Santos', 'role': 'SALES'},
            {'email': 'obra@demo.cv', 'first_name': 'Pedro', 'last_name': 'Lima', 'role': 'FOREMAN'},
            {'email': 'cliente1@demo.cv', 'first_name': 'Ana', 'last_name': 'Oliveira', 'role': 'CLIENT'},
            {'email': 'cliente2@demo.cv', 'first_name': 'Miguel', 'last_name': 'Ramos', 'role': 'CLIENT'},
        ]
        
        users = {}
        for data in users_data:
            user, created = User.objects.get_or_create(
                email=data['email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'role': data.get('role', 'CLIENT'),
                    'is_staff': data.get('is_staff', False),
                    'is_active': True,
                }
            )
            if created:
                user.set_password('Demo2026!')
                user.save()
            users[data['role']] = user
            
        return users

    def create_leads(self, users):
        """Create demo leads"""
        from apps.crm.models import Lead
        
        self.stdout.write('Creating leads...')
        
        leads_data = [
            {'first_name': 'Ana', 'last_name': 'Oliveira', 'email': 'ana.oliveira@email.cv', 'phone': '+2389991234', 'status': 'CONVERTED', 'source': 'WEBSITE'},
            {'first_name': 'Miguel', 'last_name': 'Ramos', 'email': 'miguel.ramos@email.cv', 'phone': '+2389995678', 'status': 'CONVERTED', 'source': 'REFERRAL'},
            {'first_name': 'Catarina', 'last_name': 'Fernandes', 'email': 'catarina.f@email.cv', 'phone': '+2389999012', 'status': 'QUALIFIED', 'source': 'SOCIAL_MEDIA'},
            {'first_name': 'Bruno', 'last_name': 'Gomes', 'email': 'bruno.gomes@email.cv', 'phone': '+2389993456', 'status': 'NEW', 'source': 'WALK_IN'},
            {'first_name': 'Sofia', 'last_name': 'Martins', 'email': 'sofia.martins@email.cv', 'phone': '+2389997890', 'status': 'CONTACTED', 'source': 'WEBSITE'},
        ]
        
        leads = []
        for data in leads_data:
            lead, created = Lead.objects.get_or_create(
                email=data['email'],
                defaults={
                    **data,
                    'assigned_to': users.get('SALES'),
                    'notes': 'Lead de demonstração criado automaticamente.',
                }
            )
            leads.append(lead)
            
        return leads

    def create_projects(self):
        """Create demo real estate projects"""
        from apps.projects.models import Project
        
        self.stdout.write('Creating projects...')
        
        projects_data = [
            {
                'name': 'Residencial Palmarejo',
                'description': 'Condomínio residencial com 24 apartamentos T2 e T3',
                'address': 'Palmarejo, Praia',
                'island': 'SANTIAGO',
                'typology': 'RESIDENTIAL',
                'total_units': 24,
                'status': 'ACTIVE',
            },
            {
                'name': 'Edifício Central',
                'description': 'Edifício comercial e residencial no centro da cidade',
                'address': 'Avenida Cidade de Lisboa, Praia',
                'island': 'SANTIAGO',
                'typology': 'MIXED',
                'total_units': 12,
                'status': 'ACTIVE',
            },
        ]
        
        projects = []
        for data in projects_data:
            project, created = Project.objects.get_or_create(
                name=data['name'],
                defaults=data
            )
            projects.append(project)
            
        return projects

    def create_units(self, projects):
        """Create demo units"""
        from apps.projects.models import Unit
        
        self.stdout.write('Creating units...')
        
        units = []
        tipologias = ['T1', 'T2', 'T2', 'T3', 'T3', 'T4']
        
        for project in projects:
            for i in range(1, project.total_units + 1):
                typology = random.choice(tipologias)
                unit, created = Unit.objects.get_or_create(
                    project=project,
                    code=f'{project.name[:3].upper()}-{i:02d}',
                    defaults={
                        'typology': typology,
                        'area_m2': random.choice([55, 75, 90, 110, 130]),
                        'price_cve': random.choice([4500000, 6500000, 8500000, 11000000, 14000000]),
                        'status': random.choice(['AVAILABLE', 'RESERVED', 'SOLD']),
                        'floor': random.randint(0, 4),
                    }
                )
                units.append(unit)
                
        return units

    def create_contracts(self, leads, units, users):
        """Create demo contracts"""
        from apps.contracts.models import Contract
        
        self.stdout.write('Creating contracts...')
        
        contracts = []
        converted_leads = [l for l in leads if l.status == 'CONVERTED']
        available_units = [u for u in units if u.status == 'SOLD']
        
        for i, lead in enumerate(converted_leads):
            if i < len(available_units):
                unit = available_units[i]
                contract, created = Contract.objects.get_or_create(
                    unit=unit,
                    defaults={
                        'lead': lead,
                        'status': 'ACTIVE',
                        'sale_price': unit.price_cve,
                        'down_payment_percent': 20,
                        'installment_months': 120,
                        'interest_rate': 8.5,
                        'signed_date': timezone.now() - timedelta(days=random.randint(30, 180)),
                    }
                )
                contracts.append(contract)
                
        return contracts

    def create_construction_projects(self, contracts, users):
        """Create demo construction projects"""
        from apps.construction.models import ConstructionProject
        
        self.stdout.write('Creating construction projects...')
        
        projects = []
        for contract in contracts:
            project, created = ConstructionProject.objects.get_or_create(
                contract=contract,
                defaults={
                    'name': f"Obra - {contract.unit.code}",
                    'description': f'Projeto de construção para {contract.unit.project.name}',
                    'start_date': timezone.now() - timedelta(days=random.randint(30, 90)),
                    'expected_end_date': timezone.now() + timedelta(days=random.randint(180, 365)),
                    'status': 'ACTIVE',
                    'overall_progress_pct': random.randint(10, 60),
                }
            )
            projects.append(project)
            
        return projects

    def create_phases_and_tasks(self, construction_projects, users):
        """Create construction phases and tasks"""
        from apps.construction.models import ConstructionPhase, ConstructionTask
        
        self.stdout.write('Creating phases and tasks...')
        
        phases_data = [
            {'name': 'Fundações', 'order': 1, 'duration_days': 30},
            {'name': 'Estrutura', 'order': 2, 'duration_days': 45},
            {'name': 'Alvenaria', 'order': 3, 'duration_days': 30},
            {'name': 'Instalações', 'order': 4, 'duration_days': 25},
            {'name': 'Acabamentos', 'order': 5, 'duration_days': 40},
            {'name': 'Pintura e Limpeza', 'order': 6, 'duration_days': 15},
        ]
        
        tasks_templates = [
            {'name': 'Escavação', 'phase': 0},
            {'name': 'Armaduras', 'phase': 0},
            {'name': 'Betão', 'phase': 0},
            {'name': 'Pilares', 'phase': 1},
            {'name': 'Vigas', 'phase': 1},
            {'name': 'Lajes', 'phase': 1},
            {'name': 'Paredes', 'phase': 2},
            {'name': 'Divisórias', 'phase': 2},
            {'name': 'Elétrica', 'phase': 3},
            {'name': 'Hidráulica', 'phase': 3},
            {'name': 'Pavimentos', 'phase': 4},
            {'name': 'Cozinha', 'phase': 4},
            {'name': 'WC', 'phase': 4},
            {'name': 'Pintura', 'phase': 5},
            {'name': 'Limpeza Final', 'phase': 5},
        ]
        
        for project in construction_projects:
            phases = []
            for phase_data in phases_data:
                phase, created = ConstructionPhase.objects.get_or_create(
                    project=project,
                    name=phase_data['name'],
                    defaults={
                        'order': phase_data['order'],
                        'start_date': project.start_date + timedelta(days=(phase_data['order']-1)*30) if project.start_date else None,
                        'status': random.choice(['COMPLETED', 'IN_PROGRESS', 'NOT_STARTED']),
                        'progress_pct': random.randint(0, 100) if phase_data['order'] <= 3 else 0,
                    }
                )
                phases.append(phase)
            
            # Create tasks for each phase
            for task_template in tasks_templates:
                phase = phases[task_template['phase']]
                is_completed = phase.status == 'COMPLETED' or (phase.status == 'IN_PROGRESS' and random.random() > 0.5)
                
                ConstructionTask.objects.get_or_create(
                    project=project,
                    phase=phase,
                    name=task_template['name'],
                    defaults={
                        'status': 'COMPLETED' if is_completed else 'TODO',
                        'progress_pct': 100 if is_completed else random.randint(0, 50),
                        'assigned_to': users.get('FOREMAN'),
                        'start_date': phase.start_date,
                        'due_date': phase.start_date + timedelta(days=10) if phase.start_date else None,
                    }
                )

    def create_budgets(self, construction_projects):
        """Create demo budgets"""
        from apps.budget.models import SimpleBudget, BudgetItem
        
        self.stdout.write('Creating budgets...')
        
        categories = [
            ('Materiais', ['Cimento', 'Tijolos', 'Areia', 'Brita', 'Ferro', 'Madeira', 'Cerâmica']),
            ('Mão de Obra', ['Pedreiros', 'Carpinteiros', 'Eletricistas', 'Hidráulicos', 'Pintores']),
            ('Equipamentos', [' betoneira', 'Andaimes', 'Gerador', 'Compressor']),
            ('Transporte', ['Camionagem', 'Aluguer de equipamentos']),
        ]
        
        for project in construction_projects:
            budget, created = SimpleBudget.objects.get_or_create(
                project=project,
                defaults={
                    'name': f'Orçamento - {project.name}',
                    'total_budget': 5000000,
                    'status': 'APPROVED',
                }
            )
            
            if created:
                for category, items in categories:
                    for item_name in items:
                        BudgetItem.objects.create(
                            budget=budget,
                            category=category,
                            item_name=item_name,
                            unit='UN' if category == 'Equipamentos' else random.choice(['KG', 'M2', 'M3', 'UN']),
                            quantity=random.randint(10, 500),
                            unit_price=random.randint(100, 5000),
                            actual_cost=random.randint(500, 25000),
                        )

    def create_daily_reports(self, construction_projects, users):
        """Create demo daily reports"""
        from apps.construction.models import DailyReport
        
        self.stdout.write('Creating daily reports...')
        
        for project in construction_projects:
            # Create 10-20 daily reports
            for i in range(random.randint(10, 20)):
                date = timezone.now() - timedelta(days=i*7)
                DailyReport.objects.get_or_create(
                    project=project,
                    date=date.date(),
                    defaults={
                        'progress_pct': min(100, max(0, project.overall_progress_pct - (i*2))),
                        'summary': f'Relatório de progresso - Semana {i+1}',
                        'description': random.choice([
                            'Trabalhos de fundação avançados.',
                            'Concretagem de pilares concluída.',
                            'Instalações elétricas em andamento.',
                            'Pavimentação iniciada.',
                            'Acabamentos em progresso.',
                        ]),
                        'status': 'APPROVED',
                        'created_by': users.get('FOREMAN'),
                    }
                )

    def print_summary(self):
        """Print summary of created data"""
        from apps.construction.models import ConstructionProject, ConstructionTask
        from apps.contracts.models import Contract
        from apps.crm.models import Lead
        from apps.projects.models import Unit
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.NOTICE('DEMO DATA SUMMARY'))
        self.stdout.write('='*50)
        self.stdout.write(f"Leads: {Lead.objects.count()}")
        self.stdout.write(f"Units: {Unit.objects.count()}")
        self.stdout.write(f"Contracts: {Contract.objects.count()}")
        self.stdout.write(f"Construction Projects: {ConstructionProject.objects.count()}")
        self.stdout.write(f"Tasks: {ConstructionTask.objects.count()}")
        self.stdout.write('='*50)
