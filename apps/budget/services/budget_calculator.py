"""
Budget Calculator — Cálculos de orçamento.

Fornece funcionalidades para:
- Criar orçamentos a partir de templates
- Comparar versões de orçamentos
- Calcular estatísticas e resumos
"""
from decimal import Decimal
from typing import List, Dict, Optional
from django.db import transaction
from django.utils import timezone

from apps.budget.models import (
    SimpleBudget, BudgetItem, LocalPriceItem
)


class BudgetCalculator:
    """
    Calculadora de orçamentos com suporte a templates e comparações.
    """
    
    # Templates predefinidos para tipos comuns de projectos
    TEMPLATES = {
        'residential_t2': {
            'name': 'Orçamento Tipo T2',
            'description': 'Orçamento base para apartamento T2',
            'items': [
                # Fundações e Estrutura
                {'category': 'MATERIALS', 'description': 'Cimento CP350 50kg', 'unit': 'SACO', 'quantity': 150, 'line_number': 1},
                {'category': 'MATERIALS', 'description': 'Tijolo 15x20x30', 'unit': 'UN', 'quantity': 8000, 'line_number': 2},
                {'category': 'MATERIALS', 'description': 'Areia média (m3)', 'unit': 'M3', 'quantity': 25, 'line_number': 3},
                {'category': 'MATERIALS', 'description': 'Brita (m3)', 'unit': 'M3', 'quantity': 15, 'line_number': 4},
                {'category': 'MATERIALS', 'description': 'Ferro 10mm', 'unit': 'KG', 'quantity': 500, 'line_number': 5},
                {'category': 'MATERIALS', 'description': 'Ferro 12mm', 'unit': 'KG', 'quantity': 800, 'line_number': 6},
                {'category': 'MATERIALS', 'description': 'Ferro 16mm', 'unit': 'KG', 'quantity': 600, 'line_number': 7},
                # Cobertura
                {'category': 'MATERIALS', 'description': 'Telha de fibrocimento', 'unit': 'UN', 'quantity': 120, 'line_number': 8},
                {'category': 'MATERIALS', 'description': 'Madeira para caibros', 'unit': 'ML', 'quantity': 80, 'line_number': 9},
                # Instalações
                {'category': 'MATERIALS', 'description': 'Tubo PVC 100mm', 'unit': 'ML', 'quantity': 30, 'line_number': 10},
                {'category': 'MATERIALS', 'description': 'Tubo PVC 50mm', 'unit': 'ML', 'quantity': 40, 'line_number': 11},
                {'category': 'MATERIALS', 'description': 'Fio eléctrico 2.5mm', 'unit': 'ML', 'quantity': 200, 'line_number': 12},
                {'category': 'MATERIALS', 'description': 'Caixa de distribuição', 'unit': 'UN', 'quantity': 1, 'line_number': 13},
                # Acabamentos
                {'category': 'MATERIALS', 'description': 'Cerâmica piso (m2)', 'unit': 'M2', 'quantity': 60, 'line_number': 14},
                {'category': 'MATERIALS', 'description': 'Azulejo parede (m2)', 'unit': 'M2', 'quantity': 40, 'line_number': 15},
                {'category': 'MATERIALS', 'description': 'Tinta látex (L)', 'unit': 'L', 'quantity': 50, 'line_number': 16},
                {'category': 'MATERIALS', 'description': 'Porta interior completa', 'unit': 'UN', 'quantity': 4, 'line_number': 17},
                {'category': 'MATERIALS', 'description': 'Porta exterior completa', 'unit': 'UN', 'quantity': 1, 'line_number': 18},
                {'category': 'MATERIALS', 'description': 'Janela alumínio', 'unit': 'UN', 'quantity': 6, 'line_number': 19},
                # Mão-de-obra
                {'category': 'LABOR', 'description': 'Pedreiro', 'unit': 'DAY', 'quantity': 60, 'line_number': 20},
                {'category': 'LABOR', 'description': 'Carpinteiro', 'unit': 'DAY', 'quantity': 20, 'line_number': 21},
                {'category': 'LABOR', 'description': 'Eletricista', 'unit': 'DAY', 'quantity': 15, 'line_number': 22},
                {'category': 'LABOR', 'description': 'Canalizador', 'unit': 'DAY', 'quantity': 10, 'line_number': 23},
                {'category': 'LABOR', 'description': 'Pintor', 'unit': 'DAY', 'quantity': 12, 'line_number': 24},
                {'category': 'LABOR', 'description': 'Servente', 'unit': 'DAY', 'quantity': 40, 'line_number': 25},
            ]
        },
        'residential_t3': {
            'name': 'Orçamento Tipo T3',
            'description': 'Orçamento base para apartamento T3',
            'items': [
                # Fundações e Estrutura (maior quantidade que T2)
                {'category': 'MATERIALS', 'description': 'Cimento CP350 50kg', 'unit': 'SACO', 'quantity': 200, 'line_number': 1},
                {'category': 'MATERIALS', 'description': 'Tijolo 15x20x30', 'unit': 'UN', 'quantity': 12000, 'line_number': 2},
                {'category': 'MATERIALS', 'description': 'Areia média (m3)', 'unit': 'M3', 'quantity': 35, 'line_number': 3},
                {'category': 'MATERIALS', 'description': 'Brita (m3)', 'unit': 'M3', 'quantity': 20, 'line_number': 4},
                {'category': 'MATERIALS', 'description': 'Ferro 10mm', 'unit': 'KG', 'quantity': 700, 'line_number': 5},
                {'category': 'MATERIALS', 'description': 'Ferro 12mm', 'unit': 'KG', 'quantity': 1000, 'line_number': 6},
                {'category': 'MATERIALS', 'description': 'Ferro 16mm', 'unit': 'KG', 'quantity': 800, 'line_number': 7},
                # Cobertura
                {'category': 'MATERIALS', 'description': 'Telha de fibrocimento', 'unit': 'UN', 'quantity': 160, 'line_number': 8},
                {'category': 'MATERIALS', 'description': 'Madeira para caibros', 'unit': 'ML', 'quantity': 100, 'line_number': 9},
                # Instalações
                {'category': 'MATERIALS', 'description': 'Tubo PVC 100mm', 'unit': 'ML', 'quantity': 40, 'line_number': 10},
                {'category': 'MATERIALS', 'description': 'Tubo PVC 50mm', 'unit': 'ML', 'quantity': 50, 'line_number': 11},
                {'category': 'MATERIALS', 'description': 'Fio eléctrico 2.5mm', 'unit': 'ML', 'quantity': 280, 'line_number': 12},
                {'category': 'MATERIALS', 'description': 'Fio eléctrico 4mm', 'unit': 'ML', 'quantity': 50, 'line_number': 13},
                {'category': 'MATERIALS', 'description': 'Caixa de distribuição', 'unit': 'UN', 'quantity': 1, 'line_number': 14},
                # Acabamentos
                {'category': 'MATERIALS', 'description': 'Cerâmica piso (m2)', 'unit': 'M2', 'quantity': 85, 'line_number': 15},
                {'category': 'MATERIALS', 'description': 'Azulejo parede (m2)', 'unit': 'M2', 'quantity': 55, 'line_number': 16},
                {'category': 'MATERIALS', 'description': 'Tinta látex (L)', 'unit': 'L', 'quantity': 70, 'line_number': 17},
                {'category': 'MATERIALS', 'description': 'Porta interior completa', 'unit': 'UN', 'quantity': 5, 'line_number': 18},
                {'category': 'MATERIALS', 'description': 'Porta exterior completa', 'unit': 'UN', 'quantity': 2, 'line_number': 19},
                {'category': 'MATERIALS', 'description': 'Janela alumínio', 'unit': 'UN', 'quantity': 8, 'line_number': 20},
                # Mão-de-obra
                {'category': 'LABOR', 'description': 'Pedreiro', 'unit': 'DAY', 'quantity': 80, 'line_number': 21},
                {'category': 'LABOR', 'description': 'Carpinteiro', 'unit': 'DAY', 'quantity': 25, 'line_number': 22},
                {'category': 'LABOR', 'description': 'Eletricista', 'unit': 'DAY', 'quantity': 20, 'line_number': 23},
                {'category': 'LABOR', 'description': 'Canalizador', 'unit': 'DAY', 'quantity': 15, 'line_number': 24},
                {'category': 'LABOR', 'description': 'Pintor', 'unit': 'DAY', 'quantity': 16, 'line_number': 25},
                {'category': 'LABOR', 'description': 'Servente', 'unit': 'DAY', 'quantity': 55, 'line_number': 26},
            ]
        },
        'commercial_small': {
            'name': 'Orçamento Comercial (Pequeno)',
            'description': 'Orçamento base para loja ou escritório pequeno (~50m2)',
            'items': [
                {'category': 'MATERIALS', 'description': 'Cimento CP350 50kg', 'unit': 'SACO', 'quantity': 80, 'line_number': 1},
                {'category': 'MATERIALS', 'description': 'Tijolo 15x20x30', 'unit': 'UN', 'quantity': 3000, 'line_number': 2},
                {'category': 'MATERIALS', 'description': 'Areia média (m3)', 'unit': 'M3', 'quantity': 12, 'line_number': 3},
                {'category': 'MATERIALS', 'description': 'Ferro 10mm', 'unit': 'KG', 'quantity': 200, 'line_number': 4},
                {'category': 'MATERIALS', 'description': 'Ferro 12mm', 'unit': 'KG', 'quantity': 300, 'line_number': 5},
                {'category': 'MATERIALS', 'description': 'Cerâmica piso (m2)', 'unit': 'M2', 'quantity': 50, 'line_number': 6},
                {'category': 'MATERIALS', 'description': 'Fio eléctrico 2.5mm', 'unit': 'ML', 'quantity': 150, 'line_number': 7},
                {'category': 'MATERIALS', 'description': 'Fio eléctrico 6mm', 'unit': 'ML', 'quantity': 30, 'line_number': 8},
                {'category': 'MATERIALS', 'description': 'Porta comercial completa', 'unit': 'UN', 'quantity': 2, 'line_number': 9},
                {'category': 'MATERIALS', 'description': 'Persiana metálica', 'unit': 'UN', 'quantity': 1, 'line_number': 10},
                {'category': 'LABOR', 'description': 'Pedreiro', 'unit': 'DAY', 'quantity': 30, 'line_number': 11},
                {'category': 'LABOR', 'description': 'Eletricista', 'unit': 'DAY', 'quantity': 10, 'line_number': 12},
                {'category': 'LABOR', 'description': 'Servente', 'unit': 'DAY', 'quantity': 20, 'line_number': 13},
            ]
        },
    }
    
    def create_budget_from_template(
        self, 
        project_id: int, 
        template_type: str,
        user,
        island: str = 'SANTIAGO',
        custom_name: Optional[str] = None
    ) -> SimpleBudget:
        """
        Criar orçamento baseado em template.
        
        Args:
            project_id: ID do projecto
            template_type: Tipo de template ('residential_t2', 'residential_t3', 'commercial_small')
            user: Utilizador que cria o orçamento
            island: Ilha para preços
            custom_name: Nome personalizado (opcional)
            
        Returns:
            SimpleBudget criado
        """
        if template_type not in self.TEMPLATES:
            raise ValueError(f'Template desconhecido: {template_type}')
        
        template = self.TEMPLATES[template_type]
        
        # Determinar próxima versão
        base_name = custom_name or template['name']
        existing = SimpleBudget.objects.filter(
            project_id=project_id,
            name=base_name
        ).count()
        version = f'{existing + 1}.0'
        
        with transaction.atomic():
            # Criar orçamento
            budget = SimpleBudget.objects.create(
                project_id=project_id,
                name=base_name,
                version=version,
                description=template['description'],
                island=island,
                created_by=user,
                status=SimpleBudget.STATUS_DRAFT
            )
            
            # Criar items do template
            for item_data in template['items']:
                # Buscar preço da base de dados
                unit_price = self._get_unit_price(
                    item_data['description'],
                    item_data['category'],
                    island,
                    item_data['unit']
                )
                
                BudgetItem.objects.create(
                    budget=budget,
                    category=item_data['category'],
                    description=item_data['description'],
                    line_number=item_data['line_number'],
                    quantity=item_data['quantity'],
                    unit=item_data['unit'],
                    unit_price=unit_price,
                    price_source=BudgetItem.PRICE_SOURCE_DATABASE if unit_price > 0 else BudgetItem.PRICE_SOURCE_MANUAL
                )
            
            # Recalcular totais
            budget.recalculate_totals()
        
        return budget
    
    def _get_unit_price(
        self, 
        description: str, 
        category: str, 
        island: str,
        unit: str
    ) -> Decimal:
        """Buscar preço unitário na base de dados."""
        # Tentar encontrar item correspondente
        from apps.budget.services import PriceEngine
        engine = PriceEngine()
        
        suggestion = engine.suggest_price(description, island, category, unit)
        
        if suggestion['suggested_price']:
            return Decimal(str(suggestion['suggested_price']))
        
        # Fallback: retornar 0 para preenchimento manual
        return Decimal('0.00')
    
    def compare_versions(
        self, 
        budget_id: int, 
        version_a: str, 
        version_b: str
    ) -> Dict:
        """
        Comparar duas versões do orçamento.
        
        Args:
            budget_id: ID do orçamento base
            version_a: Primeira versão a comparar
            version_b: Segunda versão a comparar
            
        Returns:
            Dicionário com diferenças entre versões
        """
        try:
            budget_a = SimpleBudget.objects.get(
                id=budget_id,
                version=version_a
            )
            budget_b = SimpleBudget.objects.get(
                id=budget_id, 
                version=version_b
            )
        except SimpleBudget.DoesNotExist:
            raise ValueError('Uma ou ambas as versões não existem')
        
        items_a = {item.description: item for item in budget_a.items.all()}
        items_b = {item.description: item for item in budget_b.items.all()}
        
        all_descriptions = set(items_a.keys()) | set(items_b.keys())
        
        changes = []
        for desc in all_descriptions:
            item_a = items_a.get(desc)
            item_b = items_b.get(desc)
            
            if item_a and item_b:
                # Item existe em ambas as versões — verificar alterações
                changes_detected = []
                if item_a.quantity != item_b.quantity:
                    changes_detected.append(f'Qtd: {item_a.quantity} → {item_b.quantity}')
                if item_a.unit_price != item_b.unit_price:
                    changes_detected.append(f'Preço: {item_a.unit_price} → {item_b.unit_price}')
                if item_a.total != item_b.total:
                    changes_detected.append(f'Total: {item_a.total} → {item_b.total}')
                
                if changes_detected:
                    changes.append({
                        'type': 'modified',
                        'description': desc,
                        'line_number': item_a.line_number,
                        'changes': changes_detected
                    })
            elif item_a and not item_b:
                # Item removido
                changes.append({
                    'type': 'removed',
                    'description': desc,
                    'line_number': item_a.line_number,
                    'quantity': float(item_a.quantity),
                    'total': float(item_a.total)
                })
            elif item_b and not item_a:
                # Item adicionado
                changes.append({
                    'type': 'added',
                    'description': desc,
                    'line_number': item_b.line_number,
                    'quantity': float(item_b.quantity),
                    'total': float(item_b.total)
                })
        
        # Calcular diferenças totais
        total_diff = budget_b.grand_total - budget_a.grand_total
        total_diff_pct = (
            (total_diff / budget_a.grand_total) * 100 
            if budget_a.grand_total > 0 else 0
        )
        
        return {
            'version_a': version_a,
            'version_b': version_b,
            'comparison_date': timezone.now().isoformat(),
            'summary': {
                'items_added': sum(1 for c in changes if c['type'] == 'added'),
                'items_removed': sum(1 for c in changes if c['type'] == 'removed'),
                'items_modified': sum(1 for c in changes if c['type'] == 'modified'),
            },
            'totals': {
                'version_a': float(budget_a.grand_total),
                'version_b': float(budget_b.grand_total),
                'difference': float(total_diff),
                'difference_pct': round(float(total_diff_pct), 2)
            },
            'changes': changes
        }
    
    def duplicate_budget(
        self, 
        budget_id: int, 
        user,
        new_name: Optional[str] = None,
        increment_version: bool = True
    ) -> SimpleBudget:
        """
        Duplicar um orçamento existente.
        
        Args:
            budget_id: ID do orçamento a duplicar
            user: Utilizador que cria a cópia
            new_name: Novo nome (opcional)
            increment_version: Se deve incrementar versão
            
        Returns:
            Novo SimpleBudget
        """
        original = SimpleBudget.objects.get(id=budget_id)
        
        # Determinar nome e versão
        name = new_name or original.name
        if increment_version:
            version_parts = original.version.split('.')
            new_version = f'{version_parts[0]}.{int(version_parts[1]) + 1}'
        else:
            new_version = original.version
        
        with transaction.atomic():
            # Criar novo orçamento
            new_budget = SimpleBudget.objects.create(
                project=original.project,
                name=name,
                version=new_version,
                description=original.description,
                island=original.island,
                currency=original.currency,
                contingency_pct=original.contingency_pct,
                created_by=user,
                status=SimpleBudget.STATUS_DRAFT
            )
            
            # Copiar items
            for item in original.items.all():
                BudgetItem.objects.create(
                    budget=new_budget,
                    category=item.category,
                    description=item.description,
                    line_number=item.line_number,
                    quantity=item.quantity,
                    unit=item.unit,
                    unit_price=item.unit_price,
                    price_source=item.price_source,
                    notes=item.notes
                )
            
            # Recalcular totais
            new_budget.recalculate_totals()
        
        return new_budget
    
    def get_budget_summary(self, budget_id: int) -> Dict:
        """
        Obter resumo estatístico do orçamento.
        
        Args:
            budget_id: ID do orçamento
            
        Returns:
            Dicionário com estatísticas
        """
        budget = SimpleBudget.objects.get(id=budget_id)
        items = budget.items.all()
        
        # Estatísticas por categoria
        categories = {}
        for category_code, category_name in LocalPriceItem.CATEGORIES:
            cat_items = [i for i in items if i.category == category_code]
            if cat_items:
                categories[category_code] = {
                    'name': category_name,
                    'item_count': len(cat_items),
                    'total': float(sum(i.total for i in cat_items)),
                    'percentage': round(
                        float(sum(i.total for i in cat_items) / budget.subtotal * 100), 2
                    ) if budget.subtotal > 0 else 0
                }
        
        # Top 10 items mais caros
        top_items = sorted(items, key=lambda x: x.total, reverse=True)[:10]
        
        return {
            'budget_id': str(budget.id),
            'budget_name': budget.name,
            'version': budget.version,
            'status': budget.status,
            'island': budget.island,
            'summary': {
                'total_items': len(items),
                'categories': categories,
                'top_expensive_items': [
                    {
                        'description': item.description,
                        'category': item.category,
                        'quantity': float(item.quantity),
                        'unit_price': float(item.unit_price),
                        'total': float(item.total)
                    }
                    for item in top_items
                ]
            },
            'financial': {
                'total_materials': float(budget.total_materials),
                'total_labor': float(budget.total_labor),
                'total_equipment': float(budget.total_equipment),
                'total_services': float(budget.total_services),
                'subtotal': float(budget.subtotal),
                'contingency': float(budget.total_contingency),
                'contingency_pct': float(budget.contingency_pct),
                'grand_total': float(budget.grand_total)
            }
        }
