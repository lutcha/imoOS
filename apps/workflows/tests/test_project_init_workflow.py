"""
Tests for Project Initialization Workflow — Contrato → Projeto de Obra.
"""
import pytest
from datetime import date

from apps.workflows.services.project_init_workflow import ProjectInitWorkflow
from apps.construction.models import ConstructionPhase, ConstructionTask
from apps.contracts.models import Contract


@pytest.mark.django_db
def test_create_construction_project_success(
    tenant_context, contract_factory, user_factory, construction_project_model
):
    """Test successful project initialization from contract."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        from apps.construction.models import ConstructionProject
        
        user = user_factory()
        contract = contract_factory(status=Contract.STATUS_ACTIVE)
        
        result = ProjectInitWorkflow.create_construction_project(
            contract_id=str(contract.id),
            user=user,
            start_date=date(2026, 6, 1)
        )
        
        assert result['success'] is True
        assert 'project_id' in result
        assert result['phases_created'] == 6  # DEFAULT_PHASES count
        assert result['tasks_created'] > 0
        
        # Verify project created
        project = ConstructionProject.objects.get(id=result['project_id'])
        assert project.contract == contract
        assert project.status == 'IN_PROGRESS'
        assert project.start_planned == date(2026, 6, 1)
        
        # Verify phases created
        phases = ConstructionPhase.objects.filter(project=project.project)
        assert phases.count() == 6
        
        # Verify tasks created
        tasks = ConstructionTask.objects.filter(project=project.project)
        assert tasks.count() == result['tasks_created']


@pytest.mark.django_db
def test_create_construction_project_contract_not_active(
    tenant_context, contract_factory, user_factory
):
    """Test project init fails if contract not active."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        user = user_factory()
        contract = contract_factory(status=Contract.STATUS_DRAFT)
        
        result = ProjectInitWorkflow.create_construction_project(
            contract_id=str(contract.id),
            user=user
        )
        
        assert result['success'] is False
        assert 'assinado' in result['error'].lower() or 'activo' in result['error'].lower()


@pytest.mark.django_db
def test_create_construction_project_already_exists(
    tenant_context, contract_factory, user_factory, construction_project_factory
):
    """Test project init fails if project already exists."""
    tenant, schema_name = tenant_context
    
    with tenant_context(tenant):
        from apps.construction.models import ConstructionProject
        
        user = user_factory()
        contract = contract_factory(status=Contract.STATUS_ACTIVE)
        
        # Create existing project
        existing = construction_project_factory(contract=contract)
        
        result = ProjectInitWorkflow.create_construction_project(
            contract_id=str(contract.id),
            user=user
        )
        
        assert result['success'] is False
        assert 'já existe' in result['error'].lower()
        assert result['project_id'] == str(existing.id)


@pytest.fixture
def construction_project_model():
    """Fixture to ensure ConstructionProject model exists."""
    try:
        from apps.construction.models import ConstructionProject
        return ConstructionProject
    except ImportError:
        pytest.skip("ConstructionProject model not yet available")


@pytest.fixture
def construction_project_factory():
    """Factory for ConstructionProject."""
    try:
        from apps.construction.models import ConstructionProject
        
        def factory(**kwargs):
            defaults = {
                'name': 'Test Project',
                'status': 'PLANNING',
                'start_planned': date(2026, 6, 1),
            }
            defaults.update(kwargs)
            return ConstructionProject.objects.create(**defaults)
        
        return factory
    except ImportError:
        return None
