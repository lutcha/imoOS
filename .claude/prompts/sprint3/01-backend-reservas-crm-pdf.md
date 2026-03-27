# Sprint 3 — Backend: Reservas + CRM Pipeline + Proposta PDF

## Pré-requisitos

Ler estes ficheiros antes de começar:
- `apps/inventory/models.py` — Unit (status choices, FK para Floor)
- `apps/crm/models.py` — Lead (campos existentes)
- `apps/memberships/models.py` — TenantMembership (roles)
- `apps/core/models.py` — TenantAwareModel (herdar daqui)

## Skills a carregar

```
@.claude/skills/08-module-crm/reservation-lock-mechanism/SKILL.md
@.claude/skills/08-module-crm/lead-qualification-flow/SKILL.md
@.claude/skills/08-module-crm/visit-scheduling-calendar/SKILL.md
@.claude/skills/08-module-crm/proposal-generation-pdf/SKILL.md
@.claude/skills/08-module-crm/commission-calculation/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/01-multi-tenant/cross-tenant-prevention/SKILL.md
```

## Agents a activar (por esta ordem)

| Agent | Tarefa | Prompt sugerido |
|-------|--------|----------------|
| `model-architect` | Criar `UnitReservation` | "Cria modelo UnitReservation para ImoOS. Deve herdar de TenantAwareModel, ter FK para Unit e Lead, expiração automática via campo `expires_at`, estado (ACTIVE/EXPIRED/CONVERTED/CANCELLED), e HistoricalRecords. Garantir que Unit.status e UnitReservation ficam sincronizados." |
| `tenant-expert` | Auditar lógica de reserva | "Audita o `ReservationViewSet` e o método `create_reservation`. Verifica: (1) SELECT FOR UPDATE usado correctamente, (2) lead.unit e unit.status actualizados na mesma transacção, (3) nenhum cross-tenant possível." |
| `drf-viewset-builder` | Gerar ReservationViewSet | "Gera ReservationViewSet com actions: `create_reservation` (POST, usa SELECT FOR UPDATE), `cancel` (POST), `convert_to_contract` (POST). Permission: IsTenantMember. Incluir testes de isolamento." |
| `isolation-test-writer` | Testes anti-double-booking | "Escreve testes de isolamento para UnitReservation: (1) dois requests simultâneos para a mesma unidade — apenas um deve ter sucesso, (2) reserva de tenant_a não visível em tenant_b, (3) cancel liberta a unidade correctamente." |

---

## Tarefa 1 — `apps/crm/models.py` — Adicionar campos ao Lead

Ler o ficheiro existente. O modelo já tem `first_name`, `last_name`, `email`, `status`, `source`, etc.

Adicionar (sem remover nada existente):
```python
# Pipeline stage para o Kanban
STAGE_NEW = 'new'
STAGE_CONTACTED = 'contacted'
STAGE_VISIT_SCHEDULED = 'visit_scheduled'
STAGE_PROPOSAL_SENT = 'proposal_sent'
STAGE_NEGOTIATION = 'negotiation'
STAGE_WON = 'won'
STAGE_LOST = 'lost'

STAGE_CHOICES = [
    (STAGE_NEW, 'Novo'),
    (STAGE_CONTACTED, 'Contactado'),
    (STAGE_VISIT_SCHEDULED, 'Visita Agendada'),
    (STAGE_PROPOSAL_SENT, 'Proposta Enviada'),
    (STAGE_NEGOTIATION, 'Negociação'),
    (STAGE_WON, 'Ganho'),
    (STAGE_LOST, 'Perdido'),
]

stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default=STAGE_NEW)
lost_reason = models.TextField(blank=True)
visit_date = models.DateTimeField(null=True, blank=True)
proposal_sent_at = models.DateTimeField(null=True, blank=True)
commission_rate = models.DecimalField(
    max_digits=5, decimal_places=2, default=Decimal('3.00'),
    help_text='% comissão do vendedor'
)
```

---

## Tarefa 2 — `apps/crm/models.py` — Criar `UnitReservation`

```python
class UnitReservation(TenantAwareModel):
    """
    Reserva de uma unidade para um lead.
    Previne double-booking via SELECT FOR UPDATE em create_reservation().
    Uma unidade só pode ter uma reserva ACTIVE de cada vez.
    """
    STATUS_ACTIVE = 'ACTIVE'
    STATUS_EXPIRED = 'EXPIRED'
    STATUS_CONVERTED = 'CONVERTED'   # → contrato assinado
    STATUS_CANCELLED = 'CANCELLED'

    STATUS_CHOICES = [
        (STATUS_ACTIVE, 'Activa'),
        (STATUS_EXPIRED, 'Expirada'),
        (STATUS_CONVERTED, 'Convertida em Contrato'),
        (STATUS_CANCELLED, 'Cancelada'),
    ]

    unit = models.ForeignKey(
        'inventory.Unit', on_delete=models.CASCADE, related_name='reservations'
    )
    lead = models.ForeignKey(
        'crm.Lead', on_delete=models.CASCADE, related_name='reservations'
    )
    reserved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='+'
    )
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    expires_at = models.DateTimeField(help_text='Reserva expira automaticamente')
    deposit_amount_cve = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal('0.00')
    )
    notes = models.TextField(blank=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        # Garantia de unicidade — só uma reserva ACTIVE por unidade
        constraints = [
            models.UniqueConstraint(
                fields=['unit'],
                condition=models.Q(status='ACTIVE'),
                name='unique_active_reservation_per_unit',
            )
        ]
```

---

## Tarefa 3 — `apps/crm/views.py` — Adicionar actions ao LeadViewSet

Ler o `views.py` existente. Adicionar ao `LeadViewSet` existente:

```python
@action(detail=True, methods=['patch'], url_path='move-stage')
def move_stage(self, request, pk=None):
    """Mover lead para o próximo stage do pipeline (Kanban drag)."""

@action(detail=True, methods=['post'], url_path='schedule-visit')
def schedule_visit(self, request, pk=None):
    """Agendar visita — define visit_date e move stage para visit_scheduled."""

@action(detail=True, methods=['post'], url_path='send-proposal')
def send_proposal(self, request, pk=None):
    """Gerar proposta PDF e registar envio. Usar task Celery."""
```

**Novo `ReservationViewSet`** (ficheiro separado ou no mesmo views.py):
```python
class ReservationViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsTenantMember]

    @action(detail=False, methods=['post'], url_path='create-reservation')
    def create_reservation(self, request):
        """
        Criar reserva com SELECT FOR UPDATE — previne double-booking.
        Segue skill: reservation-lock-mechanism
        """
        from django.db import transaction

        unit_id = request.data.get('unit_id')
        lead_id = request.data.get('lead_id')

        with transaction.atomic():
            # SELECT FOR UPDATE — bloqueia a linha durante a transacção
            unit = Unit.objects.select_for_update().get(
                id=unit_id, status=Unit.STATUS_AVAILABLE
            )
            # Se chegámos aqui, a unidade está disponível e bloqueada
            unit.status = Unit.STATUS_RESERVED
            unit.save(update_fields=['status', 'updated_at'])

            reservation = UnitReservation.objects.create(
                unit=unit,
                lead_id=lead_id,
                reserved_by=request.user,
                expires_at=...,
            )

        return Response(ReservationSerializer(reservation).data, status=201)
```

---

## Tarefa 4 — Celery task: gerar proposta PDF

**`apps/crm/tasks.py`** — ler o ficheiro existente, adicionar nova task:

```python
@shared_task(
    bind=True,
    max_retries=3,
    name='crm.generate_proposal_pdf',
)
def generate_proposal_pdf(self, *, tenant_schema: str, lead_id: str, unit_id: str) -> dict:
    """
    Gera PDF de proposta de compra com WeasyPrint e faz upload para S3.
    Retorna URL público (ou presigned) do PDF gerado.
    Segue skills: proposal-generation-pdf, celery-safe-pattern
    """
```

Template HTML base em: `apps/crm/templates/crm/proposal.html`
- Logótipo do tenant (de `TenantSettings.logo_url`)
- Dados da unidade (código, tipologia, área, preço CVE/EUR, planta)
- Dados do lead (nome, contacto)
- Cláusulas legais (placeholder para Cabo Verde)
- Footer: data, referência, assinatura do vendedor

---

## Tarefa 5 — `apps/crm/urls.py` — Actualizar com novas rotas

Ler o `urls.py` existente antes de editar.
Adicionar `ReservationViewSet` ao router e a route pública `lead-capture/`.

---

## Verificação final

- [ ] `python manage.py check` sem erros
- [ ] `pytest tests/tenant_isolation/ -v` — todos passing (incluindo novos testes de reserva)
- [ ] `POST /api/v1/crm/reservations/create-reservation/` com unit disponível → 201, unit.status=RESERVED
- [ ] `POST /api/v1/crm/reservations/create-reservation/` simultâneo para a mesma unit → apenas um 201, outro 400
- [ ] `PATCH /api/v1/crm/leads/{id}/move-stage/` actualiza `stage` e `history`
- [ ] Task `generate_proposal_pdf` gera PDF e faz upload para S3 (em staging)
