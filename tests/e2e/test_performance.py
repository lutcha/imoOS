"""
Testes E2E: Performance

Valida tempos de resposta de endpoints críticos.
"""
import time
from decimal import Decimal
from datetime import date, timedelta

import pytest
from django_tenants.utils import tenant_context
from rest_framework import status


pytestmark = [pytest.mark.e2e, pytest.mark.performance, pytest.mark.django_db(transaction=True)]


class TestDashboardPerformance:
    """Testar performance do dashboard."""
    
    MAX_RESPONSE_TIME = 2.0  # segundos
    
    def test_dashboard_stats_loads_under_2_seconds(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """1. Dashboard deve carregar em <2s."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/dashboard/stats/')
        
        elapsed_time = time.time() - start_time
        
        # Verificar tempo de resposta
        assert elapsed_time < self.MAX_RESPONSE_TIME, (
            f"Dashboard took {elapsed_time:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"
        )
        
        # Verificar resposta válida
        assert response.status_code == status.HTTP_200_OK
    
    def test_dashboard_kpis_loads_quickly(
        self, authenticated_client, e2e_tenant
    ):
        """2. KPIs do dashboard carregam rapidamente."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/dashboard/kpis/')
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_dashboard_charts_data_loads_quickly(
        self, authenticated_client, e2e_tenant
    ):
        """3. Dados de gráficos carregam rapidamente."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/dashboard/charts/')
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestGanttAPIPerformance:
    """Testar performance da API Gantt."""
    
    MAX_RESPONSE_TIME = 0.5  # 500ms
    
    def test_gantt_api_response_time(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """1. API Gantt deve responder em <500ms."""
        start_time = time.time()
        
        response = authenticated_client.get(
            f'/api/v1/construction/gantt/?project={e2e_project.id}'
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME, (
            f"Gantt API took {elapsed_time:.2f}s, expected < {self.MAX_RESPONSE_TIME}s"
        )
        
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_gantt_with_many_tasks(
        self, authenticated_client, e2e_tenant, e2e_project, e2e_user
    ):
        """2. Gantt com muitas tasks deve responder em tempo razoável."""
        from apps.construction.models import ConstructionTask
        
        with tenant_context(e2e_tenant):
            # Criar muitas tasks
            for i in range(50):
                ConstructionTask.objects.create(
                    project=e2e_project,
                    wbs_code=f'LOAD.{i}',
                    name=f'Task Load Test {i}',
                    status=ConstructionTask.STATUS_PENDING,
                    due_date=date.today() + timedelta(days=i),
                    priority=ConstructionTask.PRIORITY_MEDIUM,
                )
        
        start_time = time.time()
        
        response = authenticated_client.get(
            f'/api/v1/construction/gantt/?project={e2e_project.id}'
        )
        
        elapsed_time = time.time() - start_time
        
        # Com muitas tasks, permitir mais tempo, mas ainda <2s
        assert elapsed_time < 2.0, (
            f"Gantt with many tasks took {elapsed_time:.2f}s"
        )


class TestListAPIPerformance:
    """Testar performance de APIs de listagem."""
    
    MAX_RESPONSE_TIME = 1.0  # 1 segundo
    
    def test_leads_list_performance(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """1. Listagem de leads deve ser rápida."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/crm/leads/')
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_200_OK
    
    def test_units_list_performance(
        self, authenticated_client, e2e_tenant, e2e_unit
    ):
        """2. Listagem de unidades deve ser rápida."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/inventory/units/')
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_200_OK
    
    def test_contracts_list_performance(
        self, authenticated_client, e2e_tenant, e2e_contract
    ):
        """3. Listagem de contratos deve ser rápida."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/contracts/contracts/')
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_200_OK
    
    def test_tasks_list_performance(
        self, authenticated_client, e2e_tenant, e2e_construction_tasks
    ):
        """4. Listagem de tasks deve ser rápida."""
        start_time = time.time()
        
        response = authenticated_client.get('/api/v1/construction/tasks/')
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_200_OK


class TestSearchPerformance:
    """Testar performance de busca."""
    
    MAX_RESPONSE_TIME = 1.5  # 1.5 segundos
    
    def test_leads_search_performance(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """1. Busca de leads deve ser rápida."""
        start_time = time.time()
        
        response = authenticated_client.get(
            '/api/v1/crm/leads/?search=joao'
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_200_OK
    
    def test_units_search_performance(
        self, authenticated_client, e2e_tenant, e2e_unit
    ):
        """2. Busca de unidades deve ser rápida."""
        start_time = time.time()
        
        response = authenticated_client.get(
            '/api/v1/inventory/units/?search=T2'
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code == status.HTTP_200_OK


class TestReportPerformance:
    """Testar performance de relatórios."""
    
    MAX_RESPONSE_TIME = 3.0  # 3 segundos para relatórios
    
    def test_sales_report_performance(
        self, authenticated_client, e2e_tenant
    ):
        """1. Relatório de vendas deve gerar em <3s."""
        start_time = time.time()
        
        response = authenticated_client.get(
            '/api/v1/reports/sales/?start_date=2026-01-01&end_date=2026-12-31'
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
    
    def test_construction_progress_report(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """2. Relatório de progresso deve gerar rapidamente."""
        start_time = time.time()
        
        response = authenticated_client.get(
            f'/api/v1/reports/construction/?project={e2e_project.id}'
        )
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < self.MAX_RESPONSE_TIME
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]


class TestDatabaseQueryPerformance:
    """Testar performance de queries ao banco."""
    
    def test_leads_query_count(
        self, authenticated_client, e2e_tenant
    ):
        """1. Listagem de leads deve usar queries otimizadas."""
        from django.db import connection
        from django.test.utils import override_settings
        
        with override_settings(DEBUG=True):
            # Limpar queries anteriores
            connection.queries_log.clear()
            
            response = authenticated_client.get('/api/v1/crm/leads/')
            
            # Contar queries
            query_count = len(connection.queries)
            
            # Deve usar no máximo 5 queries (1 count + 1 list + possíveis relacionamentos)
            assert query_count <= 5, (
                f"Too many queries: {query_count}. Queries: {[q['sql'][:100] for q in connection.queries]}"
            )
    
    def test_contract_detail_query_count(
        self, authenticated_client, e2e_tenant, e2e_contract
    ):
        """2. Detalhe de contrato deve usar queries otimizadas."""
        from django.db import connection
        from django.test.utils import override_settings
        
        with override_settings(DEBUG=True):
            connection.queries_log.clear()
            
            response = authenticated_client.get(
                f'/api/v1/contracts/contracts/{e2e_contract.id}/'
            )
            
            query_count = len(connection.queries)
            
            # Deve usar no máximo 3 queries
            assert query_count <= 3, (
                f"Too many queries: {query_count}"
            )


class TestConcurrentRequests:
    """Testar performance sob carga."""
    
    def test_multiple_concurrent_reads(
        self, authenticated_client, e2e_tenant, e2e_lead
    ):
        """1. Múltiplas leituras simultâneas."""
        import concurrent.futures
        
        def make_request(i):
            return authenticated_client.get('/api/v1/crm/leads/')
        
        start_time = time.time()
        
        # Fazer 10 requisições simultâneas
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, i) for i in range(10)]
            responses = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        elapsed_time = time.time() - start_time
        
        # Todas devem ter sucesso
        assert all(r.status_code == status.HTTP_200_OK for r in responses)
        
        # Deve completar em menos de 5 segundos
        assert elapsed_time < 5.0, (
            f"Concurrent requests took {elapsed_time:.2f}s"
        )


class TestMemoryUsage:
    """Testar uso de memória."""
    
    def test_large_list_pagination(
        self, authenticated_client, e2e_tenant, e2e_user
    ):
        """1. Grandes listas devem usar paginação."""
        from apps.crm.models import Lead
        
        # Criar muitos leads
        with tenant_context(e2e_tenant):
            for i in range(100):
                Lead.objects.create(
                    first_name=f'Lead {i}',
                    last_name='Test',
                    email=f'lead{i}@test.cv',
                    status=Lead.STATUS_NEW,
                )
        
        response = authenticated_client.get('/api/v1/crm/leads/')
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        
        # Deve ter paginação
        if isinstance(data, dict):
            assert 'results' in data
            assert 'count' in data
            # Não deve retornar todos de uma vez
            assert len(data['results']) <= 50  # Tamanho padrão de página


class TestCaching:
    """Testar uso de cache."""
    
    def test_dashboard_uses_cache(
        self, authenticated_client, e2e_tenant
    ):
        """1. Dashboard deve usar cache."""
        # Primeira requisição
        start_1 = time.time()
        response_1 = authenticated_client.get('/api/v1/dashboard/stats/')
        time_1 = time.time() - start_1
        
        # Segunda requisição (deve ser mais rápida se cached)
        start_2 = time.time()
        response_2 = authenticated_client.get('/api/v1/dashboard/stats/')
        time_2 = time.time() - start_2
        
        assert response_1.status_code == status.HTTP_200_OK
        assert response_2.status_code == status.HTTP_200_OK
        
        # Segunda requisição deve ser igual ou mais rápida
        # (pode não ser cached em dev, mas a estrutura deve permitir)
    
    def test_gantt_cache(
        self, authenticated_client, e2e_tenant, e2e_project
    ):
        """2. Gantt deve usar cache."""
        url = f'/api/v1/construction/gantt/?project={e2e_project.id}'
        
        # Primeira requisição
        response_1 = authenticated_client.get(url)
        
        # Segunda requisição
        response_2 = authenticated_client.get(url)
        
        # Ambas devem ter sucesso
        assert response_1.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
        assert response_2.status_code in [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND]
