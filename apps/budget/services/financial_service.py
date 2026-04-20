"""
Financial Consolidation Service — Cálculos de Budget vs Actual e Rentabilidade.
"""
from django.db.models import Sum
from apps.budget.models import SimpleBudget, ConstructionExpense, ConstructionAdvance
from apps.projects.models import Project

class FinancialConsolidationService:
    """Serviço para consolidar dados financeiros de projectos."""
    
    def get_project_financial_status(self, project_id):
        """
        Retorna o estado financeiro consolidado do projecto.
        """
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return None
        
        # 1. Obter Orçamento Aprovado (Baseline)
        budget = SimpleBudget.objects.filter(
            project=project,
            status=SimpleBudget.STATUS_APPROVED
        ).order_by('-version').first()
        
        # Se não houver aprovado, usa o mais recente (draft)
        if not budget:
            budget = SimpleBudget.objects.filter(project=project).order_by('-version').first()
            
        budget_total = float(budget.grand_total) if budget else 0.0
        
        # 2. Obter Gastos Reais (Expenses)
        # Apenas despesas pagas ou aprovadas
        actual_expenses = ConstructionExpense.objects.filter(
            project=project,
            status=ConstructionExpense.STATUS_PAID
        ).aggregate(total=Sum('amount_cve'))['total'] or 0.0
        
        actual_expenses = float(actual_expenses)
        
        # 3. Obter Adiantamentos em Aberto (Pending Advances)
        pending_advances = ConstructionAdvance.objects.filter(
            project=project,
            is_settled=False
        ).aggregate(total=Sum('amount_cve'))['total'] or 0.0
        
        pending_advances = float(pending_advances)
        
        # 4. Calcular Desvio (Variance)
        variance = actual_expenses - budget_total
        variance_pct = (variance / budget_total * 100) if budget_total > 0 else 0
        
        # 5. Granularidade por Categoria (Budget vs Actual)
        categories = []
        for cat_code, cat_name in ConstructionExpense.CATEGORIES:
            cat_budget = 0.0
            if budget:
                if cat_code == 'MATERIALS': cat_budget = float(budget.total_materials)
                elif cat_code == 'LABOR': cat_budget = float(budget.total_labor)
                elif cat_code == 'EQUIPMENT': cat_budget = float(budget.total_equipment)
                elif cat_code == 'SERVICES': cat_budget = float(budget.total_services)
            
            cat_actual = ConstructionExpense.objects.filter(
                project=project,
                category=cat_code,
                status=ConstructionExpense.STATUS_PAID
            ).aggregate(total=Sum('amount_cve'))['total'] or 0.0
            
            categories.append({
                'category': cat_code,
                'name': cat_name,
                'budget': float(cat_budget),
                'actual': float(cat_actual),
                'variance': float(cat_actual) - float(cat_budget)
            })
            
        return {
            'project_name': project.name,
            'budget_total_cve': budget_total,
            'actual_total_cve': actual_expenses,
            'pending_advances_cve': pending_advances,
            'variance_cve': variance,
            'variance_pct': round(variance_pct, 2),
            'currency_cve': 'CVE',
            'currency_eur': 'EUR',
            'eur_rate': 110.265,
            'categories': categories
        }
