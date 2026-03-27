"""
Payments module — Tenant schema.

Adds structured payment plans on top of the flat Contract.payments list.
A PaymentPlan splits a contract's total into:
  - 1 × DEPOSIT  (10% sinal)
  - N × INSTALLMENT  (80% / N, monthly)
  - 1 × FINAL  (10% escritura)

Each PaymentPlanItem carries a deterministic MBE reference so the buyer
can pay via Multibanco at any ATM or online.
"""

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import models
from simple_history.models import HistoricalRecords

from apps.core.models import TenantAwareModel
from apps.payments.mbe import generate_mbe_reference


class PaymentPlan(TenantAwareModel):
    """
    Structured payment schedule linked 1-to-1 with a Contract.

    Lifecycle:
        Contract signed → PaymentPlan.generate() → PaymentPlanItems created
        Item paid → linked to a contracts.Payment record

    Idempotency: generate_standard() deletes existing items before re-creating,
    so calling it twice is safe.
    """

    TYPE_STANDARD = 'STANDARD'  # 10 % deposit + 80 % instalments + 10 % final
    TYPE_CUSTOM = 'CUSTOM'       # Manually edited plan

    TYPE_CHOICES = [
        (TYPE_STANDARD, 'Padrão (10/80/10)'),
        (TYPE_CUSTOM, 'Personalizado'),
    ]

    contract = models.OneToOneField(
        'contracts.Contract',
        on_delete=models.CASCADE,
        related_name='payment_plan',
        verbose_name='Contrato',
    )
    plan_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default=TYPE_STANDARD,
        verbose_name='Tipo de plano',
    )
    total_cve = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor total (CVE)',
    )
    notes = models.TextField(blank=True, verbose_name='Notas')

    history = HistoricalRecords()

    class Meta:
        app_label = 'payments'
        verbose_name = 'Plano de Pagamento'
        verbose_name_plural = 'Planos de Pagamento'
        ordering = ['-created_at']

    def __str__(self):
        return f'Plano {self.contract.contract_number} ({self.get_plan_type_display()})'

    def generate_standard(self, installments: int = 8, start_date: date | None = None) -> None:
        """
        Generate STANDARD plan items:
          - DEPOSIT (10%) — due in 7 days from start_date
          - INSTALLMENT × N (80% / N each) — monthly from deposit due date
          - FINAL (10%) — 1 month after last installment

        Idempotent: deletes existing items before re-generating.
        MBE references are computed deterministically from contract_id + order.

        Args:
            installments: Number of monthly instalments (default 8).
            start_date: Base date for schedule (defaults to today).
        """
        from dateutil.relativedelta import relativedelta

        if start_date is None:
            start_date = (
                self.contract.signed_at.date()
                if self.contract.signed_at
                else date.today()
            )

        # Clear existing items — regenerate is idempotent
        self.items.all().delete()

        contract_id = str(self.contract.id)
        total = self.total_cve

        # --- DEPOSIT (10%) ---
        deposit_pct = Decimal('10.00')
        deposit_amount = (total * deposit_pct / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        deposit_due = start_date + relativedelta(days=7)

        deposit_item = PaymentPlanItem.objects.create(
            plan=self,
            item_type=PaymentPlanItem.TYPE_DEPOSIT,
            percentage=deposit_pct,
            amount_cve=deposit_amount,
            due_date=deposit_due,
            order=0,
            mbe_reference=generate_mbe_reference(contract_id, 0, int(deposit_amount)),
        )

        # --- INSTALLMENTS (80% / N each) ---
        installment_total_pct = Decimal('80.00')
        installment_pct = (installment_total_pct / installments).quantize(
            Decimal('0.0001'), rounding=ROUND_HALF_UP
        )
        # Compute per-installment amount; last instalment absorbs rounding
        unit_amount = (total * installment_pct / 100).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        installment_total_amount = (total * installment_total_pct / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )

        for i in range(installments):
            order = i + 1
            if i == installments - 1:
                # Last instalment absorbs any rounding difference
                paid_so_far = unit_amount * (installments - 1)
                amount = installment_total_amount - paid_so_far
            else:
                amount = unit_amount

            PaymentPlanItem.objects.create(
                plan=self,
                item_type=PaymentPlanItem.TYPE_INSTALLMENT,
                percentage=installment_pct,
                amount_cve=amount,
                due_date=deposit_due + relativedelta(months=order),
                order=order,
                mbe_reference=generate_mbe_reference(contract_id, order, int(amount)),
            )

        # --- FINAL (10%) ---
        final_pct = Decimal('10.00')
        final_amount = total - deposit_amount - installment_total_amount
        # Ensure final amount is never negative due to rounding
        final_amount = max(final_amount, Decimal('0.01'))
        final_order = installments + 1
        final_due = deposit_due + relativedelta(months=installments + 1)

        PaymentPlanItem.objects.create(
            plan=self,
            item_type=PaymentPlanItem.TYPE_FINAL,
            percentage=final_pct,
            amount_cve=final_amount,
            due_date=final_due,
            order=final_order,
            mbe_reference=generate_mbe_reference(contract_id, final_order, int(final_amount)),
        )


class PaymentPlanItem(TenantAwareModel):
    """
    A single line in a PaymentPlan schedule.

    When the buyer makes the payment, the `payment` FK is linked to the
    corresponding contracts.Payment record (created by PaymentViewSet.mark_paid).
    """

    TYPE_DEPOSIT = 'DEPOSIT'
    TYPE_INSTALLMENT = 'INSTALLMENT'
    TYPE_FINAL = 'FINAL'

    TYPE_CHOICES = [
        (TYPE_DEPOSIT, 'Sinal'),
        (TYPE_INSTALLMENT, 'Prestação'),
        (TYPE_FINAL, 'Pagamento Final'),
    ]

    plan = models.ForeignKey(
        PaymentPlan,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Plano',
    )
    item_type = models.CharField(
        max_length=15,
        choices=TYPE_CHOICES,
        verbose_name='Tipo',
    )
    percentage = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        verbose_name='Percentagem (%)',
    )
    amount_cve = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name='Valor (CVE)',
    )
    due_date = models.DateField(verbose_name='Data prevista')
    payment = models.OneToOneField(
        'contracts.Payment',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plan_item',
        verbose_name='Pagamento liquidado',
    )
    mbe_reference = models.CharField(
        max_length=25,
        blank=True,
        verbose_name='Referência MBE',
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name='Ordem')

    history = HistoricalRecords()

    class Meta:
        app_label = 'payments'
        verbose_name = 'Item do Plano de Pagamento'
        verbose_name_plural = 'Itens do Plano de Pagamento'
        ordering = ['order', 'due_date']
        indexes = [
            models.Index(fields=['plan', 'order'], name='planitem_plan_order_idx'),
            models.Index(fields=['due_date'], name='planitem_due_date_idx'),
        ]

    def __str__(self):
        return f'{self.get_item_type_display()} — {self.amount_cve} CVE ({self.due_date})'

    @property
    def is_paid(self) -> bool:
        return self.payment_id is not None
