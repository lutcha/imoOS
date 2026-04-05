"""
Budget models tests.
"""
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model

from apps.budget.models import (
    LocalPriceItem, SimpleBudget, BudgetItem,
    CrowdsourcedPrice, UserPriceScore
)
from apps.projects.models import Project

User = get_user_model()


class LocalPriceItemModelTest(TestCase):
    """Testes para o modelo LocalPriceItem."""
    
    def setUp(self):
        self.price_item = LocalPriceItem.objects.create(
            category=LocalPriceItem.CATEGORY_MATERIALS,
            code='CV-001',
            name='Cimento CP350 50kg',
            description='Cimento Portland 350kg',
            unit=LocalPriceItem.UNIT_SACO,
            price_santiago=Decimal('850.00'),
            price_sao_vicente=Decimal('875.00'),
            price_sal=Decimal('900.00'),
            source='Cimpor CV',
            is_verified=True
        )
    
    def test_str_representation(self):
        """Testar representação string."""
        self.assertEqual(str(self.price_item), 'CV-001 - Cimento CP350 50kg')
    
    def test_get_price_for_island_santiago(self):
        """Testar preço para Santiago."""
        price = self.price_item.get_price_for_island('SANTIAGO')
        self.assertEqual(price, Decimal('850.00'))
    
    def test_get_price_for_island_sao_vicente(self):
        """Testar preço para São Vicente."""
        price = self.price_item.get_price_for_island('SAO_VICENTE')
        self.assertEqual(price, Decimal('875.00'))
    
    def test_get_price_for_island_fallback(self):
        """Testar fallback para Santiago quando ilha não tem preço."""
        price = self.price_item.get_price_for_island('BRAVA')
        self.assertEqual(price, Decimal('850.00'))  # Fallback Santiago
    
    def test_get_all_island_prices(self):
        """Testar obter todos os preços por ilha."""
        prices = self.price_item.get_all_island_prices()
        self.assertEqual(prices['SANTIAGO'], Decimal('850.00'))
        self.assertEqual(prices['SAO_VICENTE'], Decimal('875.00'))
        self.assertIsNone(prices['BRAVA'])


class SimpleBudgetModelTest(TestCase):
    """Testes para o modelo SimpleBudget."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Projecto Teste',
            slug='projecto-teste'
        )
        self.budget = SimpleBudget.objects.create(
            project=self.project,
            name='Orçamento Teste',
            version='1.0',
            island='SANTIAGO',
            created_by=self.user,
            contingency_pct=Decimal('10.00')
        )
        
        # Criar items de teste
        BudgetItem.objects.create(
            budget=self.budget,
            line_number=1,
            category=LocalPriceItem.CATEGORY_MATERIALS,
            description='Cimento',
            quantity=Decimal('10.000'),
            unit=LocalPriceItem.UNIT_SACO,
            unit_price=Decimal('850.00')
        )
        BudgetItem.objects.create(
            budget=self.budget,
            line_number=2,
            category=LocalPriceItem.CATEGORY_LABOR,
            description='Pedreiro',
            quantity=Decimal('5.000'),
            unit=LocalPriceItem.UNIT_DAY,
            unit_price=Decimal('2500.00')
        )
    
    def test_str_representation(self):
        """Testar representação string."""
        expected = 'Orçamento Teste (v1.0) - Projecto Teste'
        self.assertEqual(str(self.budget), expected)
    
    def test_recalculate_totals(self):
        """Testar recálculo de totais."""
        self.budget.recalculate_totals()
        
        # Materiais: 10 * 850 = 8500
        self.assertEqual(self.budget.total_materials, Decimal('8500.00'))
        
        # Mão-de-obra: 5 * 2500 = 12500
        self.assertEqual(self.budget.total_labor, Decimal('12500.00'))
        
        # Subtotal: 8500 + 12500 = 21000
        self.assertEqual(self.budget.subtotal, Decimal('21000.00'))
        
        # Contingência: 10% de 21000 = 2100
        self.assertEqual(self.budget.total_contingency, Decimal('2100.00'))
        
        # Total geral: 21000 + 2100 = 23100
        self.assertEqual(self.budget.grand_total, Decimal('23100.00'))
    
    def test_get_item_count(self):
        """Testar contagem de items."""
        self.assertEqual(self.budget.get_item_count(), 2)
    
    def test_approve(self):
        """Testar aprovação do orçamento."""
        self.budget.approve(self.user)
        
        self.assertEqual(self.budget.status, SimpleBudget.STATUS_APPROVED)
        self.assertEqual(self.budget.approved_by, self.user)


class BudgetItemModelTest(TestCase):
    """Testes para o modelo BudgetItem."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.project = Project.objects.create(
            name='Projecto Teste',
            slug='projecto-teste'
        )
        self.budget = SimpleBudget.objects.create(
            project=self.project,
            name='Orçamento Teste',
            created_by=self.user
        )
    
    def test_total_calculation_on_save(self):
        """Testar cálculo automático do total ao salvar."""
        item = BudgetItem.objects.create(
            budget=self.budget,
            line_number=1,
            category=LocalPriceItem.CATEGORY_MATERIALS,
            description='Cimento',
            quantity=Decimal('10.000'),
            unit=LocalPriceItem.UNIT_SACO,
            unit_price=Decimal('850.00')
        )
        
        # Total deve ser calculado automaticamente
        self.assertEqual(item.total, Decimal('8500.00'))
    
    def test_str_representation(self):
        """Testar representação string."""
        item = BudgetItem.objects.create(
            budget=self.budget,
            line_number=5,
            category=LocalPriceItem.CATEGORY_MATERIALS,
            description='Cimento',
            quantity=Decimal('1.000'),
            unit=LocalPriceItem.UNIT_SACO,
            unit_price=Decimal('850.00')
        )
        
        self.assertEqual(str(item), '5. Cimento')


class CrowdsourcedPriceModelTest(TestCase):
    """Testes para o modelo CrowdsourcedPrice."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='reporter@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_user(
            email='admin@example.com',
            password='testpass123',
            is_staff=True
        )
        self.price = CrowdsourcedPrice.objects.create(
            reported_by=self.user,
            item_name='Cimento CP350',
            category=LocalPriceItem.CATEGORY_MATERIALS,
            price_cve=Decimal('860.00'),
            unit=LocalPriceItem.UNIT_SACO,
            location='Achada Grande, Praia',
            island='SANTIAGO',
            supplier='Cimpor Loja Praia',
            date_observed='2024-01-15'
        )
    
    def test_str_representation(self):
        """Testar representação string."""
        expected = 'Cimento CP350 - 860.00 CVE (Santiago)'
        self.assertEqual(str(self.price), expected)
    
    def test_verify_price(self):
        """Testar verificação de preço."""
        self.price.verify(self.admin, points=15)
        
        self.assertEqual(self.price.status, CrowdsourcedPrice.STATUS_VERIFIED)
        self.assertEqual(self.price.verified_by, self.admin)
        self.assertEqual(self.price.points_earned, 15)
    
    def test_reject_price(self):
        """Testar rejeição de preço."""
        self.price.reject(self.admin, 'Preço incorreto')
        
        self.assertEqual(self.price.status, CrowdsourcedPrice.STATUS_REJECTED)
        self.assertEqual(self.price.rejection_reason, 'Preço incorreto')


class UserPriceScoreModelTest(TestCase):
    """Testes para o modelo UserPriceScore."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='user@example.com',
            password='testpass123'
        )
        self.score = UserPriceScore.objects.create(
            user=self.user,
            total_points=0,
            rank=UserPriceScore.RANK_NOVATO
        )
    
    def test_str_representation(self):
        """Testar representação string."""
        expected = 'user@example.com - Novato (0 pts)'
        self.assertEqual(str(self.score), expected)
    
    def test_add_points_and_rank_update(self):
        """Testar adição de pontos e atualização de rank."""
        # Adicionar pontos suficientes para Contribuidor
        self.score.add_points(60)
        
        self.assertEqual(self.score.total_points, 60)
        self.assertEqual(self.score.prices_verified, 1)
        self.assertEqual(self.score.rank, UserPriceScore.RANK_CONTRIBUIDOR)
    
    def test_rank_progression(self):
        """Testar progressão de ranks."""
        ranks = [
            (0, UserPriceScore.RANK_NOVATO),
            (50, UserPriceScore.RANK_CONTRIBUIDOR),
            (200, UserPriceScore.RANK_ESPECIALISTA),
            (500, UserPriceScore.RANK_GURU),
            (1000, UserPriceScore.RANK_LENDA),
        ]
        
        for points, expected_rank in ranks:
            with self.subTest(points=points, rank=expected_rank):
                score = UserPriceScore.objects.create(
                    user=User.objects.create_user(email=f'user{points}@test.com'),
                    total_points=points
                )
                score._update_rank()
                self.assertEqual(score.rank, expected_rank)
