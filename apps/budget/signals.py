"""
Budget signals — Sinais Django para o app budget.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from apps.budget.models import BudgetItem, CrowdsourcedPrice, UserPriceScore


@receiver(post_save, sender=BudgetItem)
def update_budget_totals_on_save(sender, instance, created, **kwargs):
    """
    Actualizar totais do orçamento quando um item é criado ou actualizado.
    
    Nota: O cálculo do total do item é feito no método save() do modelo.
    Aqui apenas recalculamos os totais agregados do orçamento.
    """
    # Evitar recursão infinita — o recalculate_totals salva o budget
    # e isso não deve disparar este sinal novamente para os mesmos itens
    if hasattr(instance, '_skip_signal'):
        return
    
    instance.budget.recalculate_totals()


@receiver(post_delete, sender=BudgetItem)
def update_budget_totals_on_delete(sender, instance, **kwargs):
    """Actualizar totais do orçamento quando um item é eliminado."""
    instance.budget.recalculate_totals()


@receiver(post_save, sender=CrowdsourcedPrice)
def update_user_score_on_report(sender, instance, created, **kwargs):
    """
    Actualizar contador de preços reportados quando um utilizador 
    submete um novo preço.
    """
    if created:
        user_score, _ = UserPriceScore.objects.get_or_create(
            user=instance.reported_by
        )
        user_score.increment_reported()
