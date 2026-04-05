"""
Management command para seed inicial de preços de Cabo Verde.
Usage: python manage.py seed_prices [--island=SANTIAGO] [--clear]
"""
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.budget.models import PriceCategory, PriceItem


# Data inicial (50+ itens reais de Cabo Verde)
SEED_DATA = [
    # === MATERIAIS DE CONSTRUÇÃO (MAT) ===
    {'category': 'MAT', 'name': 'Cimento CP350 50kg', 'unit': 'saco', 'price_santiago': Decimal('950.00')},
    {'category': 'MAT', 'name': 'Cimento CP400 50kg', 'unit': 'saco', 'price_santiago': Decimal('1050.00')},
    {'category': 'MAT', 'name': 'Tijolo 15x20x30', 'unit': 'un', 'price_santiago': Decimal('45.00')},
    {'category': 'MAT', 'name': 'Tijolo 10x20x30', 'unit': 'un', 'price_santiago': Decimal('35.00')},
    {'category': 'MAT', 'name': 'Tijolo maciço 15x20x40', 'unit': 'un', 'price_santiago': Decimal('55.00')},
    {'category': 'MAT', 'name': 'Bloco de betão 15x20x40', 'unit': 'un', 'price_santiago': Decimal('120.00')},
    {'category': 'MAT', 'name': 'Bloco de betão 10x20x40', 'unit': 'un', 'price_santiago': Decimal('85.00')},
    {'category': 'MAT', 'name': 'Areia fina (rio)', 'unit': 'm3', 'price_santiago': Decimal('3500.00')},
    {'category': 'MAT', 'name': 'Areia grossa', 'unit': 'm3', 'price_santiago': Decimal('3200.00')},
    {'category': 'MAT', 'name': 'Brita 1', 'unit': 'm3', 'price_santiago': Decimal('4500.00')},
    {'category': 'MAT', 'name': 'Brita 2', 'unit': 'm3', 'price_santiago': Decimal('4200.00')},
    {'category': 'MAT', 'name': 'Brita 3', 'unit': 'm3', 'price_santiago': Decimal('4000.00')},
    {'category': 'MAT', 'name': 'Pedra calçada', 'unit': 'm3', 'price_santiago': Decimal('5000.00')},
    
    # Ferro e Aço
    {'category': 'MAT', 'name': 'Ferro 6mm (varão)', 'unit': 'barra', 'price_santiago': Decimal('800.00')},
    {'category': 'MAT', 'name': 'Ferro 8mm (varão)', 'unit': 'barra', 'price_santiago': Decimal('1200.00')},
    {'category': 'MAT', 'name': 'Ferro 10mm (varão)', 'unit': 'barra', 'price_santiago': Decimal('1800.00')},
    {'category': 'MAT', 'name': 'Ferro 12mm (varão)', 'unit': 'barra', 'price_santiago': Decimal('2500.00')},
    {'category': 'MAT', 'name': 'Ferro 16mm (varão)', 'unit': 'barra', 'price_santiago': Decimal('4200.00')},
    {'category': 'MAT', 'name': 'Ferro 20mm (varão)', 'unit': 'barra', 'price_santiago': Decimal('6500.00')},
    {'category': 'MAT', 'name': 'Arame de amarrar', 'unit': 'kg', 'price_santiago': Decimal('350.00')},
    
    # Madeiras
    {'category': 'MAT', 'name': 'Madeira pinho 2x3', 'unit': 'm', 'price_santiago': Decimal('250.00')},
    {'category': 'MAT', 'name': 'Madeira pinho 2x4', 'unit': 'm', 'price_santiago': Decimal('350.00')},
    {'category': 'MAT', 'name': 'Madeira pinho 2x6', 'unit': 'm', 'price_santiago': Decimal('500.00')},
    {'category': 'MAT', 'name': 'Madeira pinho 2x8', 'unit': 'm', 'price_santiago': Decimal('650.00')},
    {'category': 'MAT', 'name': 'Chapa OSB 12mm', 'unit': 'm2', 'price_santiago': Decimal('1200.00')},
    {'category': 'MAT', 'name': 'Compensado 15mm', 'unit': 'm2', 'price_santiago': Decimal('1500.00')},
    {'category': 'MAT', 'name': 'Compensado 18mm', 'unit': 'm2', 'price_santiago': Decimal('1800.00')},
    
    # Cobertura e Telhas
    {'category': 'MAT', 'name': 'Telha fibrocimento ondulada', 'unit': 'm2', 'price_santiago': Decimal('850.00')},
    {'category': 'MAT', 'name': 'Telha cerâmica portuguesa', 'unit': 'm2', 'price_santiago': Decimal('2500.00')},
    {'category': 'MAT', 'name': 'Telha de zinco ondulada', 'unit': 'm2', 'price_santiago': Decimal('1200.00')},
    {'category': 'MAT', 'name': 'Chapa zinco lisa', 'unit': 'm2', 'price_santiago': Decimal('950.00')},
    {'category': 'MAT', 'name': 'Calha de zinco', 'unit': 'm', 'price_santiago': Decimal('350.00')},
    
    # Revestimentos
    {'category': 'MAT', 'name': 'Azulejo cerâmico 20x20', 'unit': 'm2', 'price_santiago': Decimal('800.00')},
    {'category': 'MAT', 'name': 'Azulejo cerâmico 30x30', 'unit': 'm2', 'price_santiago': Decimal('1200.00')},
    {'category': 'MAT', 'name': 'Azulejo porcelânico', 'unit': 'm2', 'price_santiago': Decimal('2500.00')},
    {'category': 'MAT', 'name': 'Cerâmico piso 40x40', 'unit': 'm2', 'price_santiago': Decimal('1500.00')},
    {'category': 'MAT', 'name': 'Cerâmico piso 50x50', 'unit': 'm2', 'price_santiago': Decimal('2000.00')},
    {'category': 'MAT', 'name': 'Tijoleira tradicional', 'unit': 'm2', 'price_santiago': Decimal('1800.00')},
    
    # Pintura e Acabamentos
    {'category': 'MAT', 'name': 'Tinta látex interior 18L', 'unit': 'lata', 'price_santiago': Decimal('5500.00')},
    {'category': 'MAT', 'name': 'Tinta látex interior 3.6L', 'unit': 'lata', 'price_santiago': Decimal('1800.00')},
    {'category': 'MAT', 'name': 'Tinta exterior 18L', 'unit': 'lata', 'price_santiago': Decimal('7500.00')},
    {'category': 'MAT', 'name': 'Massa corrida 25kg', 'unit': 'saco', 'price_santiago': Decimal('1200.00')},
    {'category': 'MAT', 'name': 'Selador 18L', 'unit': 'lata', 'price_santiago': Decimal('3500.00')},
    {'category': 'MAT', 'name': 'Verniz madeira 3.6L', 'unit': 'lata', 'price_santiago': Decimal('2200.00')},
    
    # Hidráulica e Elétrica
    {'category': 'MAT', 'name': 'Tubo PVC 50mm', 'unit': 'm', 'price_santiago': Decimal('450.00')},
    {'category': 'MAT', 'name': 'Tubo PVC 75mm', 'unit': 'm', 'price_santiago': Decimal('650.00')},
    {'category': 'MAT', 'name': 'Tubo PVC 110mm', 'unit': 'm', 'price_santiago': Decimal('950.00')},
    {'category': 'MAT', 'name': 'Cabo elétrico 1.5mm', 'unit': 'm', 'price_santiago': Decimal('85.00')},
    {'category': 'MAT', 'name': 'Cabo elétrico 2.5mm', 'unit': 'm', 'price_santiago': Decimal('120.00')},
    {'category': 'MAT', 'name': 'Cabo elétrico 4mm', 'unit': 'm', 'price_santiago': Decimal('180.00')},
    {'category': 'MAT', 'name': 'Cabo elétrico 6mm', 'unit': 'm', 'price_santiago': Decimal('250.00')},
    {'category': 'MAT', 'name': 'Quadro elétrico 12 disjuntores', 'unit': 'un', 'price_santiago': Decimal('8500.00')},
    {'category': 'MAT', 'name': 'Disjuntor unipolar 16A', 'unit': 'un', 'price_santiago': Decimal('450.00')},
    {'category': 'MAT', 'name': 'Disjuntor unipolar 20A', 'unit': 'un', 'price_santiago': Decimal('450.00')},
    {'category': 'MAT', 'name': 'Disjuntor bipolar 32A', 'unit': 'un', 'price_santiago': Decimal('850.00')},
    {'category': 'MAT', 'name': 'Tomada Schuko', 'unit': 'un', 'price_santiago': Decimal('350.00')},
    {'category': 'MAT', 'name': 'Interruptor simples', 'unit': 'un', 'price_santiago': Decimal('280.00')},
    {'category': 'MAT', 'name': 'Caixa de descarga', 'unit': 'un', 'price_santiago': Decimal('8500.00')},
    {'category': 'MAT', 'name': 'Lavatório cerâmico', 'unit': 'un', 'price_santiago': Decimal('6500.00')},
    {'category': 'MAT', 'name': 'Sanita completa', 'unit': 'un', 'price_santiago': Decimal('15000.00')},
    {'category': 'MAT', 'name': 'Base de chuveiro', 'unit': 'un', 'price_santiago': Decimal('4500.00')},
    {'category': 'MAT', 'name': 'Misturadora lavatório', 'unit': 'un', 'price_santiago': Decimal('3500.00')},
    {'category': 'MAT', 'name': 'Misturadora cozinha', 'unit': 'un', 'price_santiago': Decimal('4500.00')},
    {'category': 'MAT', 'name': 'Misturadora chuveiro', 'unit': 'un', 'price_santiago': Decimal('3800.00')},
    
    # === MÃO-DE-OBRA (LABOR) ===
    {'category': 'LABOR', 'name': 'Pedreiro', 'unit': 'dia', 'price_santiago': Decimal('3500.00')},
    {'category': 'LABOR', 'name': 'Pedreiro (servente)', 'unit': 'dia', 'price_santiago': Decimal('2500.00')},
    {'category': 'LABOR', 'name': 'Carpinteiro', 'unit': 'dia', 'price_santiago': Decimal('4000.00')},
    {'category': 'LABOR', 'name': 'Serralheiro', 'unit': 'dia', 'price_santiago': Decimal('4000.00')},
    {'category': 'LABOR', 'name': 'Eletricista', 'unit': 'dia', 'price_santiago': Decimal('4500.00')},
    {'category': 'LABOR', 'name': 'Canalizador', 'unit': 'dia', 'price_santiago': Decimal('4500.00')},
    {'category': 'LABOR', 'name': 'Pintor', 'unit': 'dia', 'price_santiago': Decimal('3500.00')},
    {'category': 'LABOR', 'name': 'Ladrilhador', 'unit': 'dia', 'price_santiago': Decimal('4000.00')},
    {'category': 'LABOR', 'name': 'Encarregado', 'unit': 'dia', 'price_santiago': Decimal('6000.00')},
    {'category': 'LABOR', 'name': 'Mestre de obras', 'unit': 'dia', 'price_santiago': Decimal('8000.00')},
    {'category': 'LABOR', 'name': 'Armador de ferro', 'unit': 'dia', 'price_santiago': Decimal('3500.00')},
    {'category': 'LABOR', 'name': 'Marceneiro', 'unit': 'dia', 'price_santiago': Decimal('4000.00')},
    
    # === EQUIPAMENTOS (EQUIP) ===
    {'category': 'EQUIP', 'name': 'Grua torre', 'unit': 'dia', 'price_santiago': Decimal('15000.00')},
    {'category': 'EQUIP', 'name': 'Elevador de material', 'unit': 'dia', 'price_santiago': Decimal('8000.00')},
    {'category': 'EQUIP', 'name': 'Betoneira 250L', 'unit': 'dia', 'price_santiago': Decimal('2500.00')},
    {'category': 'EQUIP', 'name': 'Betoneira 400L', 'unit': 'dia', 'price_santiago': Decimal('3500.00')},
    {'category': 'EQUIP', 'name': 'Vibrador de betão', 'unit': 'dia', 'price_santiago': Decimal('1500.00')},
    {'category': 'EQUIP', 'name': 'Serra circular', 'unit': 'dia', 'price_santiago': Decimal('1200.00')},
    {'category': 'EQUIP', 'name': 'Serra tico-tico', 'unit': 'dia', 'price_santiago': Decimal('800.00')},
    {'category': 'EQUIP', 'name': 'Furadeira', 'unit': 'dia', 'price_santiago': Decimal('600.00')},
    {'category': 'EQUIP', 'name': 'Martelo demolidor', 'unit': 'dia', 'price_santiago': Decimal('3500.00')},
    {'category': 'EQUIP', 'name': 'Compressor de ar', 'unit': 'dia', 'price_santiago': Decimal('2500.00')},
    {'category': 'EQUIP', 'name': 'Gerador 5kVA', 'unit': 'dia', 'price_santiago': Decimal('3500.00')},
    {'category': 'EQUIP', 'name': 'Gerador 10kVA', 'unit': 'dia', 'price_santiago': Decimal('6000.00')},
    {'category': 'EQUIP', 'name': 'Andaime tubular (m2)', 'unit': 'm2', 'price_santiago': Decimal('150.00')},
    {'category': 'EQUIP', 'name': 'Caminhão de água 5000L', 'unit': 'viagem', 'price_santiago': Decimal('3500.00')},
    
    # === SERVIÇOS (SERV) ===
    {'category': 'SERV', 'name': 'Projeto arquitetônico (T1-T2)', 'unit': 'un', 'price_santiago': Decimal('150000.00')},
    {'category': 'SERV', 'name': 'Projeto arquitetônico (T3-T4)', 'unit': 'un', 'price_santiago': Decimal('250000.00')},
    {'category': 'SERV', 'name': 'Projeto estrutural', 'unit': 'un', 'price_santiago': Decimal('200000.00')},
    {'category': 'SERV', 'name': 'Projeto elétrico', 'unit': 'un', 'price_santiago': Decimal('80000.00')},
    {'category': 'SERV', 'name': 'Projeto hidráulico', 'unit': 'un', 'price_santiago': Decimal('80000.00')},
    {'category': 'SERV', 'name': 'Legalização de obra', 'unit': 'un', 'price_santiago': Decimal('50000.00')},
    {'category': 'SERV', 'name': 'Topografia', 'unit': 'un', 'price_santiago': Decimal('30000.00')},
    {'category': 'SERV', 'name': 'Sondagem geotécnica', 'unit': 'un', 'price_santiago': Decimal('45000.00')},
    {'category': 'SERV', 'name': 'Fiscalização de obra', 'unit': 'mês', 'price_santiago': Decimal('150000.00')},
    {'category': 'SERV', 'name': 'Gestão de obra', 'unit': 'mês', 'price_santiago': Decimal('200000.00')},
    {'category': 'SERV', 'name': 'Limpeza final de obra', 'unit': 'm2', 'price_santiago': Decimal('150.00')},
]

# Preços específicos para outras ilhas (variações típicas)
ISLAND_VARIATIONS = {
    'SAO_VICENTE': Decimal('1.10'),  # 10% mais caro
    'SAL': Decimal('1.25'),          # 25% mais caro (ilha turística)
    'BOA_VISTA': Decimal('1.20'),    # 20% mais caro
    'SANTO_ANTAO': Decimal('1.05'),  # 5% mais caro (transporte)
    'SAO_NICOLAU': Decimal('1.15'),  # 15% mais caro
    'MAIO': Decimal('1.20'),         # 20% mais caro
    'FOGO': Decimal('1.08'),         # 8% mais caro
    'BRAVA': Decimal('1.10'),        # 10% mais caro
}


class Command(BaseCommand):
    help = 'Seed da base de preços local para Cabo Verde'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--island',
            type=str,
            default='SANTIAGO',
            help='Ilha específica para aplicar variações de preço (default: SANTIAGO)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpar dados existentes antes de seed'
        )
        parser.add_argument(
            '--apply-variations',
            action='store_true',
            help='Aplicar variações de preço para outras ilhas'
        )
    
    def handle(self, *args, **options):
        island = options['island']
        clear_data = options['clear']
        apply_variations = options['apply_variations']
        
        self.stdout.write(self.style.NOTICE(f'Seeding preços para {island}...'))
        
        if clear_data:
            self.stdout.write(self.style.WARNING('A limpar dados existentes...'))
            PriceItem.objects.all().delete()
            PriceCategory.objects.all().delete()
        
        # Criar categorias
        categories = {
            'MAT': {'name': 'Materiais de Construção', 'icon': '🔨'},
            'LABOR': {'name': 'Mão-de-Obra', 'icon': '👷'},
            'EQUIP': {'name': 'Equipamentos', 'icon': '🚧'},
            'SERV': {'name': 'Serviços', 'icon': '📋'},
        }
        
        with transaction.atomic():
            category_objects = {}
            for code, data in categories.items():
                cat, created = PriceCategory.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': data['name'],
                        'icon': data['icon'],
                        'is_active': True
                    }
                )
                category_objects[code] = cat
                if created:
                    self.stdout.write(f'  Criada categoria: {data["name"]}')
            
            # Criar itens de preço
            created_count = 0
            updated_count = 0
            
            for item_data in SEED_DATA:
                category_code = item_data['category']
                category = category_objects.get(category_code)
                
                if not category:
                    self.stdout.write(
                        self.style.ERROR(f'Categoria {category_code} não encontrada')
                    )
                    continue
                
                price_data = {
                    'category': category,
                    'name': item_data['name'],
                    'unit': item_data['unit'],
                    'price_santiago': item_data['price_santiago'],
                    'is_active': True,
                    'is_verified': True,
                    'source': 'Admin - Seed Inicial',
                }
                
                # Aplicar variações de preço se solicitado
                if apply_variations:
                    for island_code, multiplier in ISLAND_VARIATIONS.items():
                        field_name = f'price_{island_code.lower()}'
                        varied_price = item_data['price_santiago'] * multiplier
                        # Arredondar para múltiplo de 50
                        varied_price = round(varied_price / 50) * 50
                        price_data[field_name] = varied_price
                
                # Criar ou atualizar item
                item, created = PriceItem.objects.update_or_create(
                    name=item_data['name'],
                    category=category,
                    defaults=price_data
                )
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            total = created_count + updated_count
            self.stdout.write(self.style.SUCCESS(
                f'Seed concluído! {created_count} criados, {updated_count} atualizados (total: {total})'
            ))
            
            # Estatísticas
            self.stdout.write('\nEstatísticas:')
            for code, cat in category_objects.items():
                count = PriceItem.objects.filter(category=cat).count()
                self.stdout.write(f'  {cat.icon} {cat.name}: {count} itens')
