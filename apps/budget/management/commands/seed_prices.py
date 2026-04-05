"""
Management command para seed inicial de preços de Cabo Verde.

Usage: 
    python manage.py seed_prices [--clear]
    python manage.py seed_prices --load-fixture
"""
import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.budget.models import LocalPriceItem


# Dados de seed simplificados (50 itens essenciais)
SEED_DATA = [
    # === MATERIAIS DE CONSTRUÇÃO ===
    {
        'code': 'CV-001', 'category': 'MATERIALS', 'name': 'Cimento CP350 50kg',
        'unit': 'SACO', 'price_santiago': '850.00', 'source': 'Cimpor CV'
    },
    {
        'code': 'CV-002', 'category': 'MATERIALS', 'name': 'Cimento CP450 50kg',
        'unit': 'SACO', 'price_santiago': '920.00', 'source': 'Cimpor CV'
    },
    {
        'code': 'CV-003', 'category': 'MATERIALS', 'name': 'Tijolo 15x20x30',
        'unit': 'UN', 'price_santiago': '45.00', 'source': 'Fábrica Tijolos Praia'
    },
    {
        'code': 'CV-004', 'category': 'MATERIALS', 'name': 'Tijolo 10x20x30',
        'unit': 'UN', 'price_santiago': '35.00', 'source': 'Fábrica Tijolos Praia'
    },
    {
        'code': 'CV-005', 'category': 'MATERIALS', 'name': 'Bloco de cimento 15x20x40',
        'unit': 'UN', 'price_santiago': '65.00', 'source': 'Fábrica Blocos'
    },
    {
        'code': 'CV-006', 'category': 'MATERIALS', 'name': 'Areia média (m3)',
        'unit': 'M3', 'price_santiago': '4500.00', 'source': 'Areal Santiago'
    },
    {
        'code': 'CV-007', 'category': 'MATERIALS', 'name': 'Brita 19mm (m3)',
        'unit': 'M3', 'price_santiago': '6000.00', 'source': 'Brita CV'
    },
    {
        'code': 'CV-008', 'category': 'MATERIALS', 'name': 'Brita 25mm (m3)',
        'unit': 'M3', 'price_santiago': '5800.00', 'source': 'Brita CV'
    },
    {
        'code': 'CV-009', 'category': 'MATERIALS', 'name': 'Ferro 6mm (kg)',
        'unit': 'KG', 'price_santiago': '180.00', 'source': 'Siderurgia Nacional'
    },
    {
        'code': 'CV-010', 'category': 'MATERIALS', 'name': 'Ferro 8mm (kg)',
        'unit': 'KG', 'price_santiago': '175.00', 'source': 'Siderurgia Nacional'
    },
    {
        'code': 'CV-011', 'category': 'MATERIALS', 'name': 'Ferro 10mm (kg)',
        'unit': 'KG', 'price_santiago': '170.00', 'source': 'Siderurgia Nacional'
    },
    {
        'code': 'CV-012', 'category': 'MATERIALS', 'name': 'Ferro 12mm (kg)',
        'unit': 'KG', 'price_santiago': '165.00', 'source': 'Siderurgia Nacional'
    },
    {
        'code': 'CV-013', 'category': 'MATERIALS', 'name': 'Ferro 16mm (kg)',
        'unit': 'KG', 'price_santiago': '160.00', 'source': 'Siderurgia Nacional'
    },
    {
        'code': 'CV-014', 'category': 'MATERIALS', 'name': 'Arame recozido (kg)',
        'unit': 'KG', 'price_santiago': '250.00', 'source': 'Siderurgia Nacional'
    },
    {
        'code': 'CV-015', 'category': 'MATERIALS', 'name': 'Telha fibrocimento 1.10x0.90m',
        'unit': 'UN', 'price_santiago': '850.00', 'source': 'Importado'
    },
    {
        'code': 'CV-016', 'category': 'MATERIALS', 'name': 'Madeira caibro 5x7 (ml)',
        'unit': 'ML', 'price_santiago': '180.00', 'source': 'Serralharia CV'
    },
    {
        'code': 'CV-017', 'category': 'MATERIALS', 'name': 'Tubo PVC 100mm (ml)',
        'unit': 'ML', 'price_santiago': '450.00', 'source': 'Importado'
    },
    {
        'code': 'CV-018', 'category': 'MATERIALS', 'name': 'Tubo PVC 50mm (ml)',
        'unit': 'ML', 'price_santiago': '250.00', 'source': 'Importado'
    },
    {
        'code': 'CV-019', 'category': 'MATERIALS', 'name': 'Fio elétrico 2.5mm (ml)',
        'unit': 'ML', 'price_santiago': '85.00', 'source': 'Electrão'
    },
    {
        'code': 'CV-020', 'category': 'MATERIALS', 'name': 'Fio elétrico 4mm (ml)',
        'unit': 'ML', 'price_santiago': '120.00', 'source': 'Electrão'
    },
    {
        'code': 'CV-021', 'category': 'MATERIALS', 'name': 'Cerâmica piso 45x45 (m2)',
        'unit': 'M2', 'price_santiago': '1200.00', 'source': 'Importado'
    },
    {
        'code': 'CV-022', 'category': 'MATERIALS', 'name': 'Azulejo parede 20x30 (m2)',
        'unit': 'M2', 'price_santiago': '950.00', 'source': 'Importado'
    },
    {
        'code': 'CV-023', 'category': 'MATERIALS', 'name': 'Tinta látex 18L',
        'unit': 'L', 'price_santiago': '2500.00', 'source': 'Importado'
    },
    {
        'code': 'CV-024', 'category': 'MATERIALS', 'name': 'Porta interior completa',
        'unit': 'UN', 'price_santiago': '8500.00', 'source': 'Marcenaria CV'
    },
    {
        'code': 'CV-025', 'category': 'MATERIALS', 'name': 'Porta exterior completa',
        'unit': 'UN', 'price_santiago': '15000.00', 'source': 'Importado'
    },
    {
        'code': 'CV-026', 'category': 'MATERIALS', 'name': 'Janela alumínio 1.00x1.00m',
        'unit': 'UN', 'price_santiago': '12000.00', 'source': 'Alumínios CV'
    },
    {
        'code': 'CV-027', 'category': 'MATERIALS', 'name': 'Vidro comum 4mm (m2)',
        'unit': 'M2', 'price_santiago': '1500.00', 'source': 'Importado'
    },
    {
        'code': 'CV-028', 'category': 'MATERIALS', 'name': 'Chave de porta',
        'unit': 'UN', 'price_santiago': '2500.00', 'source': 'Importado'
    },
    {
        'code': 'CV-029', 'category': 'MATERIALS', 'name': 'Cal hidratada 20kg',
        'unit': 'SACO', 'price_santiago': '450.00', 'source': 'Importado'
    },
    {
        'code': 'CV-030', 'category': 'MATERIALS', 'name': 'Prego 17x27 (kg)',
        'unit': 'KG', 'price_santiago': '350.00', 'source': 'Importado'
    },
    
    # === MÃO-DE-OBRA ===
    {
        'code': 'CV-101', 'category': 'LABOR', 'name': 'Pedreiro (dia)',
        'unit': 'DAY', 'price_santiago': '2500.00', 'source': 'Média mercado'
    },
    {
        'code': 'CV-102', 'category': 'LABOR', 'name': 'Carpinteiro (dia)',
        'unit': 'DAY', 'price_santiago': '2200.00', 'source': 'Média mercado'
    },
    {
        'code': 'CV-103', 'category': 'LABOR', 'name': 'Eletricista (dia)',
        'unit': 'DAY', 'price_santiago': '2800.00', 'source': 'Média mercado'
    },
    {
        'code': 'CV-104', 'category': 'LABOR', 'name': 'Canalizador (dia)',
        'unit': 'DAY', 'price_santiago': '2600.00', 'source': 'Média mercado'
    },
    {
        'code': 'CV-105', 'category': 'LABOR', 'name': 'Pintor (dia)',
        'unit': 'DAY', 'price_santiago': '2000.00', 'source': 'Média mercado'
    },
    {
        'code': 'CV-106', 'category': 'LABOR', 'name': 'Servente (dia)',
        'unit': 'DAY', 'price_santiago': '1500.00', 'source': 'Média mercado'
    },
    {
        'code': 'CV-107', 'category': 'LABOR', 'name': 'Serralheiro (dia)',
        'unit': 'DAY', 'price_santiago': '2400.00', 'source': 'Média mercado'
    },
    
    # === EQUIPAMENTOS ===
    {
        'code': 'CV-201', 'category': 'EQUIPMENT', 'name': 'Aluguer betoneira (dia)',
        'unit': 'DAY', 'price_santiago': '3500.00', 'source': 'Equipamentos CV'
    },
    {
        'code': 'CV-202', 'category': 'EQUIPMENT', 'name': 'Aluguer andaimes (m2/mês)',
        'unit': 'M2', 'price_santiago': '450.00', 'source': 'Equipamentos CV'
    },
    {
        'code': 'CV-203', 'category': 'EQUIPMENT', 'name': 'Aluguer escavadeira (dia)',
        'unit': 'DAY', 'price_santiago': '15000.00', 'source': 'Construção CV'
    },
    {
        'code': 'CV-204', 'category': 'EQUIPMENT', 'name': 'Bomba de concreto (hora)',
        'unit': 'HR', 'price_santiago': '8000.00', 'source': 'Construção CV'
    },
    
    # === SERVIÇOS ===
    {
        'code': 'CV-301', 'category': 'SERVICES', 'name': 'Projecto arquitectura (m2)',
        'unit': 'M2', 'price_santiago': '1500.00', 'source': 'Ordem Arquitectos'
    },
    {
        'code': 'CV-302', 'category': 'SERVICES', 'name': 'Projecto estruturas (m2)',
        'unit': 'M2', 'price_santiago': '1200.00', 'source': 'Ordem Engenheiros'
    },
    {
        'code': 'CV-303', 'category': 'SERVICES', 'name': 'Inspecção técnica',
        'unit': 'UN', 'price_santiago': '25000.00', 'source': 'Ordem Engenheiros'
    },
]


class Command(BaseCommand):
    help = 'Seed da base de preços local para Cabo Verde'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpar dados existentes antes de seed'
        )
        parser.add_argument(
            '--load-fixture',
            action='store_true',
            help='Carregar do fixture JSON completo'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Seeding preços de Cabo Verde...'))
        
        if options['clear']:
            self.stdout.write(self.style.WARNING('A limpar dados existentes...'))
            LocalPriceItem.objects.all().delete()
        
        if options['load_fixture']:
            self._load_from_fixture()
        else:
            self._load_from_seed_data()
        
        # Estatísticas
        total = LocalPriceItem.objects.count()
        materials = LocalPriceItem.objects.filter(category='MATERIALS').count()
        labor = LocalPriceItem.objects.filter(category='LABOR').count()
        equipment = LocalPriceItem.objects.filter(category='EQUIPMENT').count()
        services = LocalPriceItem.objects.filter(category='SERVICES').count()
        
        self.stdout.write(self.style.SUCCESS(f'\nSeed concluído!'))
        self.stdout.write(f'  Total de itens: {total}')
        self.stdout.write(f'  Materiais: {materials}')
        self.stdout.write(f'  Mão-de-obra: {labor}')
        self.stdout.write(f'  Equipamentos: {equipment}')
        self.stdout.write(f'  Serviços: {services}')
    
    def _load_from_seed_data(self):
        """Carregar dados do SEED_DATA."""
        with transaction.atomic():
            created_count = 0
            
            for item_data in SEED_DATA:
                # Calcular preços para outras ilhas (variação típica)
                base_price = Decimal(item_data['price_santiago'])
                variations = {
                    'sao_vicente': self._calculate_island_price(base_price, 1.03),
                    'sal': self._calculate_island_price(base_price, 1.06),
                    'boa_vista': self._calculate_island_price(base_price, 1.05),
                    'santo_antao': self._calculate_island_price(base_price, 1.04),
                    'sao_nicolau': self._calculate_island_price(base_price, 1.04),
                    'fogo': self._calculate_island_price(base_price, 1.02),
                    'brava': self._calculate_island_price(base_price, 1.05),
                    'maio': self._calculate_island_price(base_price, 1.04),
                }
                
                defaults = {
                    'category': item_data['category'],
                    'name': item_data['name'],
                    'unit': item_data['unit'],
                    'price_santiago': base_price,
                    'source': item_data['source'],
                    'is_verified': True,
                    **{f'price_{k}': v for k, v in variations.items()}
                }
                
                item, created = LocalPriceItem.objects.update_or_create(
                    code=item_data['code'],
                    defaults=defaults
                )
                
                if created:
                    created_count += 1
            
            self.stdout.write(f'  Criados: {created_count} itens')
    
    def _load_from_fixture(self):
        """Carregar do fixture JSON."""
        fixture_path = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', 'fixtures', 'cv_prices.json'
        )
        
        if not os.path.exists(fixture_path):
            self.stdout.write(
                self.style.ERROR(f'Fixture não encontrado: {fixture_path}')
            )
            return
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with transaction.atomic():
            for item in data:
                fields = item['fields']
                defaults = {
                    'category': fields['category'],
                    'name': fields['name'],
                    'description': fields.get('description', ''),
                    'unit': fields['unit'],
                    'price_santiago': fields['price_santiago'],
                    'price_sao_vicente': fields.get('price_sao_vicente') or None,
                    'price_sal': fields.get('price_sal') or None,
                    'price_boa_vista': fields.get('price_boa_vista') or None,
                    'price_santo_antao': fields.get('price_santo_antao') or None,
                    'price_sao_nicolau': fields.get('price_sao_nicolau') or None,
                    'price_fogo': fields.get('price_fogo') or None,
                    'price_brava': fields.get('price_brava') or None,
                    'price_maio': fields.get('price_maio') or None,
                    'source': fields['source'],
                    'is_verified': fields.get('is_verified', True),
                    'ifc_class': fields.get('ifc_class', ''),
                }
                
                LocalPriceItem.objects.update_or_create(
                    code=fields['code'],
                    defaults=defaults
                )
        
        self.stdout.write(f'  Carregados do fixture: {len(data)} itens')
    
    def _calculate_island_price(self, base_price: Decimal, multiplier: float) -> Decimal:
        """Calcular preço para ilha com multiplicador."""
        price = base_price * Decimal(str(multiplier))
        # Arredondar para múltiplo de 10
        return Decimal(int(price / 10) * 10)
