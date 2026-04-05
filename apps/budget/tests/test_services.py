"""
Budget services tests.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.budget.models import (
    LocalPriceItem, SimpleBudget, BudgetItem, CrowdsourcedPrice
)
from apps.budget.services import PriceEngine, BudgetCalculator
from apps.projects.models import Project

User = get_user_model()


class PriceEngineTest(TestCase):
    """Testes para o PriceEngine."""
    
    def setUp(self):
        self.engine = PriceEngine()
        
        # Criar item oficial
        self.official_item = LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-001',
            name='Cimento CP350 50kg',
            unit=LocalPriceItem.UNIT_SACO,
            price_santiago=Decimal('850.00'),
            price_sal=Decimal('900.00'),
            source='Cimpor CV',
            is_verified=True
        )
        
        # Criar item crowdsourced verificado
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        CrowdsourcedPrice.objects.create(
            reported_by=self.user,
            item_name='Cimento CP350 50kg',
            category=LocalPriceItem.CATEGORY_MATERIALS,
            price_cve=Decimal('860.00'),
            unit=LocalPriceItem.UNIT_SACO,
            location='Praia',
            island='SANTIAGO',
            date_observed='2024-01-01',
            status=CrowdsourcedPrice.STATUS_VERIFIED
        )
    
    def test_suggest_price_official_source(self):
        """Testar sugestão de preço com fonte oficial."""
        suggestion = self.engine.suggest_price(
            item_name='Cimento CP350 50kg',
            island='SANTIAGO',
            category='MATERIALS',
            unit='SACO'
        )
        
        self.assertIn('official', suggestion['sources'])
        self.assertEqual(suggestion['sources']['official']['price'], 850.00)
        self.assertEqual(suggestion['confidence'], 'high')
    
    def test_suggest_price_crowdsourced(self):
        """Testar sugestão de preço com fonte crowdsourced."""
        suggestion = self.engine.suggest_price(
            item_name='Cimento CP350 50kg',
            island='SANTIAGO',
            category='MATERIALS'
        )
        
        self.assertIn('crowdsourced', suggestion['sources'])
        self.assertEqual(suggestion['sources']['crowdsourced']['price'], 860.00)
    
    def test_suggest_price_unknown_item(self):
        """Testar sugestão para item desconhecido."""
        suggestion = self.engine.suggest_price(
            item_name='Item Inexistente XYZ',
            island='SANTIAGO',
            category='MATERIALS'
        )
        
        self.assertIsNone(suggestion['suggested_price'])
        self.assertEqual(suggestion['confidence'], 'low')
    
    def test_detect_price_anomaly_normal(self):
        """Testar detecção de preço normal (não anômalo)."""
        result = self.engine.detect_price_anomaly(
            price=Decimal('850.00'),
            item_name='Cimento CP350 50kg',
            island='SANTIAGO',
            category='MATERIALS'
        )
        
        self.assertFalse(result['is_anomaly'])
    
    def test_detect_price_anomaly_high(self):
        """Testar detecção de preço anômalo (muito alto)."""
        result = self.engine.detect_price_anomaly(
            price=Decimal('1500.00'),
            item_name='Cimento CP350 50kg',
            island='SANTIAGO',
            category='MATERIALS'
        )
        
        # Deve detectar como anômalo (muito acima da média)
        self.assertTrue(result['is_anomaly'])
        self.assertIn('acima', result['message'])
    
    def test_get_price_statistics(self):
        """Testar obtenção de estatísticas de preço."""
        # Adicionar mais preços crowdsourced
        for i, price in enumerate([840, 860, 870, 830, 850]):
            CrowdsourcedPrice.objects.create(
                reported_by=self.user,
                item_name='Cimento CP350 50kg',
                category=LocalPriceItem.CATEGORY_MATERIALS,
                price_cve=Decimal(str(price)),
                unit=LocalPriceItem.UNIT_SACO,
                location='Praia',
                island='SANTIAGO',
                date_observed='2024-01-01',
                status=CrowdsourcedPrice.STATUS_VERIFIED
            )
        
        stats = self.engine._get_price_statistics(
            item_name='Cimento CP350 50kg',
            island='SANTIAGO',
            category='MATERIALS'
        )
        
        self.assertIsNotNone(stats)
        self.assertGreaterEqual(stats['count'], 5)
        self.assertIsNotNone(stats['mean'])


class BudgetCalculatorTest(TestCase):
    """Testes para o BudgetCalculator."""
    
    def setUp(self):
        self.calculator = BudgetCalculator()
        
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Projecto Teste',
            slug='projecto-teste'
        )
        
        # Criar items de preço para o template
        LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-001',
            name='Cimento CP350 50kg',
            unit=LocalPriceItem.UNIT_SACO,
            price_santiago=Decimal('850.00'),
            source='Test',
            is_verified=True
        )
        LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_LABOR,
            code='CV-101',
            name='Pedreiro',
            unit=LocalPriceItem.UNIT_DAY,
            price_santiago=Decimal('2500.00'),
            source='Test',
            is_verified=True
        )
    
    def test_create_budget_from_template_residential_t2(self):
        """Testar criação de orçamento a partir de template T2."""
        budget = self.calculator.create_budget_from_template(
            project_id=self.project.id,
            template_type='residential_t2',
            user=self.user,
            island='SANTIAGO'
        )
        
        self.assertEqual(budget.project, self.project)
        self.assertEqual(budget.name, 'Orçamento Tipo T2')
        self.assertEqual(budget.island, 'SANTIAGO')
        self.assertGreater(budget.items.count(), 0)
    
    def test_create_budget_from_template_invalid(self):
        """Testar erro com template inválido."""
        with self.assertRaises(ValueError) as context:
            self.calculator.create_budget_from_template(
                project_id=self.project.id,
                template_type='invalid_template',
                user=self.user
            )
        
        self.assertIn('Template desconhecido', str(context.exception))
    
    def test_duplicate_budget(self):
        """Testar duplicação de orçamento."""
        # Criar orçamento original
        original = SimpleBudget.objects.create(
            project=self.project,
            name='Orçamento Original',
            version='1.0',
            created_by=self.user
        )
        BudgetItem.objects.create(
            budget=original,
            line_number=1,
            category=LocalPriceItem.CATEGORY_MATERIALS,
            description='Item Teste',
            quantity=Decimal('10.000'),
            unit=LocalPriceItem.UNIT_UN,
            unit_price=Decimal('100.00')
        )
        original.recalculate_totals()
        
        # Duplicar
        duplicate = self.calculator.duplicate_budget(
            budget_id=original.id,
            user=self.user,
            increment_version=True
        )
        
        self.assertEqual(duplicate.name, original.name)
        self.assertEqual(duplicate.version, '1.1')
        self.assertEqual(duplicate.items.count(), original.items.count())
    
    def test_get_budget_summary(self):
        """Testar obtenção de resumo do orçamento."""
        budget = SimpleBudget.objects.create(
            project=self.project,
            name='Orçamento Resumo',
            created_by=self.user
        )
        BudgetItem.objects.create(
            budget=budget,
            line_number=1,
            category=LocalPriceItem.CATEGORY_MATERIALS,
            description='Material Caro',
            quantity=Decimal('1.000'),
            unit=LocalPriceItem.UNIT_UN,
            unit_price=Decimal('10000.00')
        )
        BudgetItem.objects.create(
            budget=budget,
            line_number=2,
            category=LocalPriceItem.CATEGORY_LABOR,
            description='Mão-de-obra',
            quantity=Decimal('1.000'),
            unit=LocalPriceItem.UNIT_DAY,
            unit_price=Decimal('2500.00')
        )
        budget.recalculate_totals()
        
        summary = self.calculator.get_budget_summary(budget.id)
        
        self.assertEqual(summary['budget_name'], 'Orçamento Resumo')
        self.assertIn('categories', summary['summary'])
        self.assertEqual(summary['summary']['total_items'], 2)
        self.assertIn('financial', summary)
