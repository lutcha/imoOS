"""
Fixtures específicas para testes E2E do ImoOS.

Estas fixtures criam cenários completos que simulam
fluxos de trabalho reais dos utilizadores.
"""
import uuid
import io
from decimal import Decimal
from datetime import date, timedelta
from unittest.mock import MagicMock, patch

import pytest
from django.utils import timezone
from django_tenants.utils import tenant_context
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


# =============================================================================
# Fixtures de Cliente API
# =============================================================================

@pytest.fixture
def e2e_api_client():
    """Cliente API base para testes E2E."""
    return APIClient()


@pytest.fixture
def authenticated_client(e2e_api_client, e2e_user, e2e_tenant):
    """Cliente API autenticado para o tenant de teste."""
    refresh = RefreshToken.for_user(e2e_user)
    refresh['tenant_schema'] = e2e_tenant.schema_name
    e2e_api_client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}',
        HTTP_HOST=f'{e2e_tenant.slug}.imos.cv',
    )
    return e2e_api_client


# =============================================================================
# Fixtures de Tenant e Utilizadores
# =============================================================================

@pytest.fixture
def e2e_tenant(db):
    """
    Criar um tenant completo para testes E2E.
    
    Este fixture cria um tenant com schema próprio e
    aplica todas as migrações necessárias.
    """
    from tests.conftest import _create_test_tenant
    
    tenant = _create_test_tenant(
        db,
        schema_name='test_e2e_tenant',
        name='Empresa E2E Lda',
        slug='e2e-empresa',
        plan='pro',
        domain='e2e-empresa.imos.cv',
    )
    yield tenant
    
    from django.db import connection
    connection.set_schema_to_public()


@pytest.fixture
def e2e_user(e2e_tenant):
    """Criar utilizador admin para testes E2E."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    with tenant_context(e2e_tenant):
        user = User.objects.create_superuser(
            email='admin@e2e.cv',
            password='E2ETestPass123!',
            first_name='Admin',
            last_name='E2E',
        )
        # Criar membership no tenant
        from apps.memberships.models import Membership
        Membership.objects.create(
            user=user,
            tenant=e2e_tenant,
            role='ADMIN',
            is_active=True,
        )
    return user


@pytest.fixture
def e2e_encarregado(e2e_tenant):
    """Criar utilizador encarregado para testes."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    with tenant_context(e2e_tenant):
        user = User.objects.create_user(
            email='encarregado@e2e.cv',
            password='E2ETestPass123!',
            first_name='João',
            last_name='Encarregado',
            phone='+2389995678',
        )
    return user


@pytest.fixture
def e2e_vendedor(e2e_tenant):
    """Criar utilizador vendedor para testes."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    with tenant_context(e2e_tenant):
        user = User.objects.create_user(
            email='vendedor@e2e.cv',
            password='E2ETestPass123!',
            first_name='Maria',
            last_name='Vendedora',
            role='VENDEDOR',
        )
    return user


# =============================================================================
# Fixtures de Dados de Negócio
# =============================================================================

@pytest.fixture
def e2e_project(e2e_tenant, e2e_user):
    """Criar projeto imobiliário completo."""
    from apps.projects.models import Project, Building
    
    with tenant_context(e2e_tenant):
        project = Project.objects.create(
            name='Condomínio E2E',
            slug='condominio-e2e',
            description='Projeto para testes E2E',
            city='Praia',
            island='Santiago',
            created_by=e2e_user,
        )
        building = Building.objects.create(
            project=project,
            name='Bloco A',
            code='BLK-A',
            floors_above=4,
            floors_below=0,
        )
    return project


@pytest.fixture
def e2e_building(e2e_project):
    """Obter edifício do projeto E2E."""
    from django_tenants.utils import tenant_context
    tenant = e2e_project.tenant
    
    with tenant_context(tenant):
        return e2e_project.buildings.first()


@pytest.fixture
def e2e_floor(e2e_project, e2e_tenant):
    """Criar piso para testes."""
    from apps.projects.models import Floor
    
    with tenant_context(e2e_tenant):
        building = e2e_project.buildings.first()
        floor = Floor.objects.create(
            building=building,
            number=1,
            name='1º Andar',
        )
    return floor


@pytest.fixture
def e2e_unit(e2e_floor, e2e_tenant):
    """Criar unidade disponível para testes."""
    from apps.inventory.models import Unit, UnitType
    
    with tenant_context(e2e_tenant):
        # Criar ou obter tipologia
        unit_type, _ = UnitType.objects.get_or_create(
            name='T2',
            defaults={'code': 'T2', 'bedrooms': 2, 'bathrooms': 1}
        )
        
        unit = Unit.objects.create(
            floor=e2e_floor,
            unit_type=unit_type,
            code='T2-101',
            description='Apartamento T2 com vista mar',
            status=Unit.STATUS_AVAILABLE,
            area_bruta=Decimal('85.50'),
            area_util=Decimal('72.30'),
            orientation='Sul',
        )
        
        # Criar preço
        from apps.inventory.models import UnitPricing
        UnitPricing.objects.create(
            unit=unit,
            price_cve=Decimal('8500000.00'),
            price_eur=Decimal('77000.00'),
        )
    return unit


@pytest.fixture
def e2e_lead(e2e_tenant, e2e_vendedor):
    """Criar lead para testes."""
    from apps.crm.models import Lead
    
    with tenant_context(e2e_tenant):
        lead = Lead.objects.create(
            first_name='João',
            last_name='Silva',
            email='joao.silva@test.cv',
            phone='+2389991234',
            status=Lead.STATUS_NEW,
            stage=Lead.STAGE_NEW,
            source=Lead.SOURCE_WEB,
            assigned_to=e2e_vendedor,
            budget=Decimal('10000000.00'),
            preferred_typology='T2',
        )
    return lead


@pytest.fixture
def e2e_reservation(e2e_tenant, e2e_lead, e2e_unit, e2e_vendedor):
    """Criar reserva ativa para testes."""
    from apps.crm.models import UnitReservation
    
    with tenant_context(e2e_tenant):
        # Atualizar unidade para reservada
        e2e_unit.status = 'RESERVED'
        e2e_unit.save()
        
        reservation = UnitReservation.objects.create(
            unit=e2e_unit,
            lead=e2e_lead,
            reserved_by=e2e_vendedor,
            status=UnitReservation.STATUS_ACTIVE,
            expires_at=timezone.now() + timedelta(hours=48),
            deposit_amount_cve=Decimal('100000.00'),
            notes='Reserva para testes E2E',
        )
    return reservation


@pytest.fixture
def e2e_contract(e2e_tenant, e2e_lead, e2e_unit, e2e_vendedor):
    """Criar contrato em rascunho para testes."""
    from apps.contracts.models import Contract
    
    with tenant_context(e2e_tenant):
        contract = Contract.objects.create(
            unit=e2e_unit,
            lead=e2e_lead,
            vendor=e2e_vendedor,
            contract_number='E2E-2026-0001',
            total_price_cve=Decimal('8500000.00'),
            status=Contract.STATUS_DRAFT,
            notes='Contrato para testes E2E',
        )
    return contract


@pytest.fixture
def e2e_signed_contract(e2e_contract, e2e_tenant):
    """Criar contrato assinado para testes."""
    from apps.contracts.models import SignatureRequest
    
    with tenant_context(e2e_tenant):
        # Criar request de assinatura
        sig_request = SignatureRequest.objects.create(
            contract=e2e_contract,
            status=SignatureRequest.STATUS_SIGNED,
            signed_at=timezone.now(),
            signed_by_name='João Silva',
            ip_address='192.168.1.100',
        )
        
        # Atualizar contrato
        e2e_contract.status = e2e_contract.STATUS_ACTIVE
        e2e_contract.signed_at = timezone.now()
        e2e_contract.signature_request = sig_request
        e2e_contract.save()
    return e2e_contract


@pytest.fixture
def e2e_construction_project(e2e_signed_contract, e2e_tenant, e2e_user):
    """Criar projeto de obra vinculado a contrato assinado."""
    from apps.construction.models import ConstructionProject
    
    with tenant_context(e2e_tenant):
        project = ConstructionProject.objects.create(
            contract=e2e_signed_contract,
            project=e2e_signed_contract.unit.project,
            building=e2e_signed_contract.unit.floor.building,
            unit=e2e_signed_contract.unit,
            name=f'Obra - {e2e_signed_contract.unit.code}',
            description='Projeto de obra para testes E2E',
            status=ConstructionProject.STATUS_PLANNING,
            start_planned=date.today(),
            end_planned=date.today() + timedelta(days=180),
            created_by=e2e_user,
        )
    return project


@pytest.fixture
def e2e_construction_phases(e2e_project, e2e_tenant, e2e_user):
    """Criar fases de construção para testes."""
    from apps.construction.models import ConstructionPhase
    
    phases = []
    with tenant_context(e2e_tenant):
        phase_data = [
            ('FOUNDATION', 'Fundação', 1),
            ('STRUCTURE', 'Estrutura', 2),
            ('MASONRY', 'Alvenaria', 3),
            ('MEP', 'Instalações Hidro/Elétrica', 4),
            ('FINISHES', 'Acabamentos', 5),
            ('DELIVERY', 'Entrega', 6),
        ]
        
        for phase_type, name, order in phase_data:
            phase = ConstructionPhase.objects.create(
                project=e2e_project,
                phase_type=phase_type,
                name=f'{name} - Bloco A',
                description=f'Fase de {name}',
                start_planned=date.today() + timedelta(days=(order-1)*30),
                end_planned=date.today() + timedelta(days=order*30),
                order=order,
                created_by=e2e_user,
            )
            phases.append(phase)
    return phases


@pytest.fixture
def e2e_construction_tasks(e2e_construction_phases, e2e_tenant, e2e_project, e2e_encarregado):
    """Criar tarefas de construção para testes."""
    from apps.construction.models import ConstructionTask
    
    tasks = []
    with tenant_context(e2e_tenant):
        for phase in e2e_construction_phases:
            # Criar 3 tarefas por fase
            for i in range(1, 4):
                task = ConstructionTask.objects.create(
                    phase=phase,
                    project=e2e_project,
                    wbs_code=f'{phase.phase_type[:2]}.{i}',
                    name=f'Tarefa {i} - {phase.name}',
                    description=f'Descrição da tarefa {i}',
                    status=ConstructionTask.STATUS_PENDING,
                    due_date=phase.end_planned,
                    priority=ConstructionTask.PRIORITY_MEDIUM,
                    assigned_to=e2e_encarregado if i == 1 else None,
                    estimated_cost=Decimal('50000.00') * i,
                )
                tasks.append(task)
    return tasks


@pytest.fixture
def e2e_milestone_task(e2e_construction_phases, e2e_tenant, e2e_project, e2e_encarregado):
    """Criar uma tarefa milestone para testes de pagamento."""
    from apps.construction.models import ConstructionTask
    
    with tenant_context(e2e_tenant):
        foundation_phase = next(
            p for p in e2e_construction_phases if p.phase_type == 'FOUNDATION'
        )
        task = ConstructionTask.objects.create(
            phase=foundation_phase,
            project=e2e_project,
            wbs_code='FO.99',
            name='Conclusão da Fundação - MILESTONE',
            description='Milestone para geração de pagamento',
            status=ConstructionTask.STATUS_PENDING,
            due_date=foundation_phase.end_planned,
            priority=ConstructionTask.PRIORITY_HIGH,
            assigned_to=e2e_encarregado,
            estimated_cost=Decimal('500000.00'),
            # Indicar que é milestone (via metadata ou campo específico)
        )
        # Adicionar flag de milestone no context
        task.is_payment_milestone = True
    return task


# =============================================================================
# Fixtures de Mock
# =============================================================================

@pytest.fixture
def mock_whatsapp_service():
    """Mock do serviço WhatsApp."""
    with patch('apps.integrations.services.whatsapp_client') as mock:
        mock.send_template = MagicMock(return_value={'message_id': 'mock-msg-id'})
        mock.send_message = MagicMock(return_value={'message_id': 'mock-msg-id'})
        mock.get_message_status = MagicMock(return_value='delivered')
        yield mock


@pytest.fixture
def mock_signature_service():
    """Mock do serviço de assinatura digital."""
    with patch('apps.contracts.services.signature_service') as mock:
        mock.create_signature_request = MagicMock(return_value={
            'token': str(uuid.uuid4()),
            'url': 'https://signature.example.com/sign/mock-token',
        })
        mock.get_signature_status = MagicMock(return_value='signed')
        yield mock


@pytest.fixture
def mock_s3_storage():
    """Mock do storage S3."""
    with patch('apps.core.storage.S3Storage') as mock:
        instance = MagicMock()
        instance.upload_file = MagicMock(return_value='mock-s3-key')
        instance.get_presigned_url = MagicMock(return_value='https://s3.example.com/mock-key')
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_celery_task():
    """Mock para tasks Celery."""
    with patch('apps.workflows.tasks.execute_workflow_step') as mock:
        mock.delay = MagicMock(return_value=MagicMock(id='mock-task-id'))
        yield mock


# =============================================================================
# Fixtures de Configuração
# =============================================================================

@pytest.fixture
def e2e_settings(settings):
    """Configurações específicas para testes E2E."""
    settings.WHATSAPP_ENABLED = True
    settings.WORKFLOW_AUTO_EXECUTE = True
    settings.CELERY_TASK_ALWAYS_EAGER = True  # Executar tasks sincronamente
    return settings


# =============================================================================
# Helpers
# =============================================================================

def create_test_image(size=(2000, 2000), color='red', format='JPEG', quality=95):
    """Criar imagem de teste em memória."""
    from PIL import Image
    
    image = Image.new('RGB', size, color=color)
    image_file = io.BytesIO()
    image.save(image_file, format=format, quality=quality)
    image_file.seek(0)
    image_file.name = 'test_photo.jpg'
    return image_file


@pytest.fixture
def test_image():
    """Fornecer imagem de teste."""
    return create_test_image()


@pytest.fixture
def compressed_test_image():
    """Fornecer imagem de teste já comprimida."""
    return create_test_image(size=(800, 600), quality=60)
