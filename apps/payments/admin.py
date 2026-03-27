from django.contrib import admin

from .models import PaymentPlan, PaymentPlanItem


class PaymentPlanItemInline(admin.TabularInline):
    model = PaymentPlanItem
    extra = 0
    readonly_fields = ('mbe_reference', 'is_paid', 'created_at')
    fields = ('order', 'item_type', 'percentage', 'amount_cve', 'due_date', 'mbe_reference', 'payment', 'created_at')
    ordering = ('order',)

    @admin.display(boolean=True, description='Pago?')
    def is_paid(self, obj):
        return obj.is_paid


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ('contract', 'plan_type', 'total_cve', 'created_at')
    list_filter = ('plan_type',)
    search_fields = ('contract__contract_number',)
    readonly_fields = ('created_at', 'updated_at')
    inlines = [PaymentPlanItemInline]
