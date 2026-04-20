import csv
import io
from datetime import datetime
from django.template.loader import render_to_string
from weasyprint import HTML
from django.core.files.base import ContentFile
from apps.budget.services.financial_service import FinancialConsolidationService
from apps.budget.models import ConstructionExpense

class ConstructionReportService:
    @staticmethod
    def generate_pdf_report(project):
        """
        Generates a PDF Executive Summary for a construction project.
        """
        summary = FinancialConsolidationService.get_project_summary(project.id)
        # Get last 10 expenses for the report
        expenses = ConstructionExpense.objects.filter(project=project).order_by('-payment_date')[:10]
        
        context = {
            'project': project,
            'summary': summary,
            'expenses': expenses,
            'generated_at': datetime.now(),
        }
        
        html_string = render_to_string('budget/executive_summary.html', context)
        html = HTML(string=html_string)
        
        pdf_file = html.write_pdf()
        return pdf_file

    @staticmethod
    def generate_csv_data(project):
        """
        Generates CSV data for internal financial analysis (Excel compatible).
        """
        summary = FinancialConsolidationService.get_project_summary(project.id)
        expenses = ConstructionExpense.objects.filter(project=project).order_by('-payment_date')
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Header
        writer.writerow(['Relatorio Financeiro de Obra - ImoOS'])
        writer.writerow(['Projecto', project.name])
        writer.writerow(['Data Geracao', datetime.now().strftime('%d/%m/%Y %H:%M')])
        writer.writerow([])
        
        # Financial KPIs
        writer.writerow(['KPIs Financeiros'])
        writer.writerow(['Descricao', 'Valor (CVE)', 'Valor (EUR)'])
        writer.writerow(['Orcamento Total', summary['total_budgeted_cve'], summary['total_budgeted_eur']])
        writer.writerow(['Custo Realizado', summary['total_actual_cve'], summary['total_actual_eur']])
        writer.writerow(['Variacao (Saldo)', summary['total_variance_cve'], summary['total_variance_eur']])
        writer.writerow(['Desvio Orcamental (%)', f"{summary['performance_percentage']}%"])
        writer.writerow([])
        
        # Expenses
        writer.writerow(['Detalhamento de Despesas'])
        writer.writerow(['Data', 'Descricao', 'Categoria', 'Fornecedor', 'Valor (CVE)', 'Valor (EUR)', 'Estado'])
        
        for expense in expenses:
            writer.writerow([
                expense.payment_date.strftime('%Y-%m-%d'),
                expense.description,
                expense.get_category_display(),
                expense.supplier,
                expense.amount_cve,
                expense.amount_eur,
                expense.get_status_display()
            ])
            
        return output.getvalue()
