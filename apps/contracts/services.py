import re
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import transaction
from .models import Payment, Contract, PaymentPattern

class ContractAutomationService:
    """
    Business logic for contract automation:
    - Automated tranche generation
    - Template variable replacement
    """

    @staticmethod
    def generate_payments_from_params(contract: Contract, deposit_pct: Decimal, 
                                     final_pct: Decimal, installments_count: int, 
                                     start_date: timezone.datetime.date):
        """
        Generic logic to generate tranches based on percentages and counts.
        """
        total_cve = contract.total_price_cve
        deposit_cve = (total_cve * deposit_pct) / Decimal('100.0')
        final_cve = (total_cve * final_pct) / Decimal('100.0')
        installments_total_cve = total_cve - deposit_cve - final_cve

        payments_to_create = []

        # 1. Deposit (Sinal)
        if deposit_cve > 0:
            payments_to_create.append(Payment(
                contract=contract,
                payment_type=Payment.PAYMENT_DEPOSIT,
                amount_cve=deposit_cve,
                due_date=start_date,
                status=Payment.STATUS_PENDING,
            ))

        # 2. Installments (Prestações Mensais)
        current_date = start_date
        if installments_count > 0 and installments_total_cve > 0:
            monthly_amount = installments_total_cve / Decimal(str(installments_count))
            for _ in range(installments_count):
                current_date = current_date + relativedelta(months=1)
                payments_to_create.append(Payment(
                    contract=contract,
                    payment_type=Payment.PAYMENT_INSTALLMENT,
                    amount_cve=monthly_amount,
                    due_date=current_date,
                    status=Payment.STATUS_PENDING,
                ))

        # 3. Final Payment (Pagamento Final / Escritura)
        if final_cve > 0:
            # Final payment is usually after the last installment or at a specific milestone.
            # Here we default to one month after the last installment.
            current_date = current_date + relativedelta(months=1)
            payments_to_create.append(Payment(
                contract=contract,
                payment_type=Payment.PAYMENT_FINAL,
                amount_cve=final_cve,
                due_date=current_date,
                status=Payment.STATUS_PENDING,
            ))

        with transaction.atomic():
            # Clear existing pending payments to avoid duplicates
            contract.payments.filter(status=Payment.STATUS_PENDING).delete()
            Payment.objects.bulk_create(payments_to_create)

        return payments_to_create

    @staticmethod
    def apply_payment_pattern(contract: Contract, pattern: PaymentPattern, start_date: timezone.datetime.date):
        """
        Applies a saved pattern to a contract.
        """
        return ContractAutomationService.generate_payments_from_params(
            contract, 
            pattern.deposit_percentage, 
            pattern.final_percentage, 
            pattern.installments_count, 
            start_date
        )

    @staticmethod
    def render_contract_content(contract: Contract):
        """
        Simple variable replacement for the contract template.
        Variables: {{ lead_name }}, {{ contract_number }}, {{ total_price_cve }}, {{ unit_code }}, {{ payment_schedule_table }}
        """
        if not contract.template:
            return ""

        content = contract.template.html_content
        
        # Build payment table
        payments = contract.payments.order_by('due_date')
        table_html = "<table border='1' style='width: 100%; border-collapse: collapse;'>"
        table_html += "<tr><th>Tipo</th><th>Vencimento</th><th>Valor (CVE)</th></tr>"
        for p in payments:
            table_html += f"<tr><td>{p.get_payment_type_display()}</td><td>{p.due_date}</td><td>{p.amount_cve:,.2f}</td></tr>"
        table_html += "</table>"

        # Variable map
        variables = {
            'lead_name': f"{contract.lead.first_name} {contract.lead.last_name}",
            'contract_number': contract.contract_number,
            'total_price_cve': f"{contract.total_price_cve:,.2f}",
            'unit_code': contract.unit.code,
            'payment_schedule_table': table_html,
        }

        # Replace placeholders {{ var }}
        for key, value in variables.items():
            content = content.replace(f"{{{{ {key} }}}}", str(value))
            content = content.replace(f"{{{{{key}}}}}", str(value)) # Support both {{ var }} and {{var}}

        return content
