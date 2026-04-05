"""
Budget tenant isolation tests.

Testes críticos para garantir que não há vazamento de dados entre tenants.
"""
from decimal import Decimal
from django.test import TestCase
from django.db import connection
from django.contrib.auth import get_user_model

from apps.budget.models import (
    LocalPriceItem, SimpleBudget, BudgetItem, CrowdsourcedPrice
)
from apps.projects.models import Project
from apps.tenants.models import Client

User = get_user_model()


class BudgetTenantIsolationTest(TestCase):
    """
    Testes de isolamento entre tenants para o app budget.
    
    CRÍTICO: Estes testes garantem que:
    1. Utilizadores só veem dados do seu tenant
    2. Orçamentos não são acessíveis entre tenants
    3. Crowdsourced prices mantêm isolamento
    """
    
    def setUp(self):
        """Configurar tenants e dados de teste."""
        # Criar tenants
        self.tenant1 = Client.objects.create(
            schema_name='tenant1',
            name='Tenant 1 Test'
        )
        self.tenant2 = Client.objects.create(
            schema_name='tenant2',
            name='Tenant 2 Test'
        )
        
        # Criar utilizadores em cada tenant
        self.user_t1 = User.objects.create_user(
            email='user@tenant1.com',
            password='testpass123'
        )
        self.user_t2 = User.objects.create_user(
            email='user@tenant2.com',
            password='testpass123'
        )
    
    def _set_schema(self, schema_name):
        """Helper para mudar de schema."""
        connection.set_schema(schema_name)
    
    def test_price_item_isolation_between_tenants(self):
        """
        Testar isolamento de LocalPriceItem entre tenants.
        
        Items criados em um tenant não devem ser visíveis no outro.
        """
        # Criar item no tenant1
        self._set_schema('tenant1')
        item_t1 = LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-T1-001',
            name='Item Tenant 1',
            unit=LocalPriceItem.UNIT_UN,
            price_santiago=Decimal('100.00'),
            source='Test'
        )
        
        # Verificar que existe no tenant1
        self.assertEqual(
            LocalPriceItem.objects.filter(code='CV-T1-001').count(),
            1
        )
        
        # Mudar para tenant2 e verificar que não existe
        self._set_schema('tenant2')
        self.assertEqual(
            LocalPriceItem.objects.filter(code='CV-T1-001').count(),
            0
        )
        
        # Criar item no tenant2
        item_t2 = LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-T2-001',
            name='Item Tenant 2',
            unit=LocalPriceItem.UNIT_UN,
            price_santiago=Decimal('200.00'),
            source='Test'
        )
        
        # Verificar isolamento
        self.assertEqual(
            LocalPriceItem.objects.filter(code='CV-T2-001').count(),
            1
        )
        self.assertEqual(
            LocalPriceItem.objects.filter(code='CV-T1-001').count(),
            0
        )
    
    def test_budget_isolation_between_tenants(self):
        """
        Testar isolamento de SimpleBudget entre tenants.
        
        Orçamentos criados em um tenant não devem ser acessíveis no outro.
        """
        self._set_schema('tenant1')
        
        project_t1 = Project.objects.create(
            name='Projecto Tenant 1',
            slug='projecto-t1'
        )
        budget_t1 = SimpleBudget.objects.create(
            project=project_t1,
            name='Orçamento Tenant 1',
            created_by=self.user_t1
        )
        
        # Verificar no tenant1
        self.assertEqual(
            SimpleBudget.objects.filter(name='Orçamento Tenant 1').count(),
            1
        )
        
        # Verificar no tenant2
        self._set_schema('tenant2')
        self.assertEqual(
            SimpleBudget.objects.filter(name='Orçamento Tenant 1').count(),
            0
        )
    
    def test_budget_item_isolation_between_tenants(self):
        """
        Testar isolamento de BudgetItem entre tenants.
        """
        self._set_schema('tenant1')
        
        project_t1 = Project.objects.create(
            name='Projecto T1',
            slug='projecto-t1'
        )
        budget_t1 = SimpleBudget.objects.create(
            project=project_t1,
            name='Orçamento T1',
            created_by=self.user_t1
        )
        
        item_t1 = BudgetItem.objects.create(
            budget=budget_t1,
            line_number=1,
            category=LocalPriceItem.CATEGORY_MATERIALS,
            description='Item Secreto T1',
            quantity=Decimal('1.000'),
            unit=LocalPriceItem.UNIT_UN,
            unit_price=Decimal('1000.00')
        )
        
        # Verificar no tenant1
        self.assertEqual(
            BudgetItem.objects.filter(description='Item Secreto T1').count(),
            1
        )
        
        # Verificar no tenant2
        self._set_schema('tenant2')
        self.assertEqual(
            BudgetItem.objects.filter(description='Item Secreto T1').count(),
            0
        )
    
    def test_crowdsourced_price_isolation(self):
        """
        Testar isolamento de CrowdsourcedPrice entre tenants.
        """
        self._set_schema('tenant1')
        
        price_t1 = CrowdsourcedPrice.objects.create(
            reported_by=self.user_t1,
            item_name='Preço Secreto T1',
            category=LocalPriceItem.CATEGORY_MATERIALS,
            price_cve=Decimal('999.00'),
            unit=LocalPriceItem.UNIT_UN,
            location='Local T1',
            island='SANTIAGO',
            date_observed='2024-01-01'
        )
        
        # Verificar no tenant1
        self.assertEqual(
            CrowdsourcedPrice.objects.filter(item_name='Preço Secreto T1').count(),
            1
        )
        
        # Verificar no tenant2
        self._set_schema('tenant2')
        self.assertEqual(
            CrowdsourcedPrice.objects.filter(item_name='Preço Secreto T1').count(),
            0
        )
    
    def test_price_item_code_uniqueness_per_tenant(self):
        """
        Testar que códigos podem ser repetidos entre tenants mas não dentro.
        
        O mesmo código pode existir em tenants diferentes (isolation),
        mas deve ser único dentro de um tenant.
        """
        # Criar em tenant1
        self._set_schema('tenant1')
        LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-SHARED',
            name='Item Tenant 1',
            unit=LocalPriceItem.UNIT_UN,
            price_santiago=Decimal('100.00'),
            source='Test'
        )
        
        # Criar em tenant2 com mesmo código (deve funcionar devido ao isolation)
        self._set_schema('tenant2')
        # Nota: Em schema separado, pode ter o mesmo código
        # pois são tabelas físicas diferentes no PostgreSQL
        
        LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-SHARED',
            name='Item Tenant 2',
            unit=LocalPriceItem.UNIT_UN,
            price_santiago=Decimal('200.00'),
            source='Test'
        )
        
        # Verificar que cada tenant vê apenas o seu
        self.assertEqual(
            LocalPriceItem.objects.filter(code='CV-SHARED').count(),
            1
        )
        
        self._set_schema('tenant1')
        self.assertEqual(
            LocalPriceItem.objects.filter(code='CV-SHARED').count(),
            1
        )
    
    def tearDown(self):
        """Limpar schemas após testes."""
        # Reset para schema public
        connection.set_schema_to_public()
