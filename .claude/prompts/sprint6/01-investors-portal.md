# Sprint 6 — Portal de Investidores

## Contexto

Investidores têm acesso restrito ao ImoOS — role `investidor` no `TenantMembership`.
O portal permite consultar as suas unidades, o estado de pagamentos e documentos
associados sem aceder a dados comerciais da promotora (leads, pipeline, etc.).

O role `investidor` já existe em `TenantMembership.ROLE_INVESTIDOR = 'investidor'`.
A UI precisa de um layout alternativo — sem sidebar com CRM/Contratos/Obra.

## Pré-requisitos — Ler antes de começar

```
apps/memberships/models.py      → TenantMembership.ROLE_INVESTIDOR
apps/contracts/models.py        → Contract, Payment (já existem)
apps/users/permissions.py       → IsTenantMember (base)
apps/inventory/models.py        → Unit, status choices
frontend/src/components/layout/ → Sidebar.tsx, Topbar.tsx (layout a adaptar)
frontend/src/middleware.ts       → rotas protegidas
```

```bash
grep "investidor\|INVESTIDOR" apps/memberships/models.py apps/users/permissions.py
ls frontend/src/app/
```

## Skills a carregar

```
@.claude/skills/16-module-investors/investor-dashboard/SKILL.md
@.claude/skills/01-multi-tenant/tenant-aware-queries/SKILL.md
@.claude/skills/02-backend-django/model-audit-history/SKILL.md
@.claude/skills/04-frontend-nextjs/auth-jwt-handling/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `drf-viewset-builder` | InvestorDashboardViewSet — read-only, filtrado por user |
| `react-component-builder` | InvestorLayout + InvestorDashboard page |
| `isolation-test-writer` | Garantir que investidor não vê dados de outros |

---

## Tarefa 1 — Permission `IsInvestor`

**Ler `apps/users/permissions.py` antes de editar.**

```python
# apps/users/permissions.py — adicionar:
class IsInvestor(BasePermission):
    """Permite acesso apenas a membros com role investidor."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        from apps.memberships.models import TenantMembership
        try:
            m = TenantMembership.objects.get(user=request.user, is_active=True)
            return m.role == TenantMembership.ROLE_INVESTIDOR
        except TenantMembership.DoesNotExist:
            return False

class IsInvestorOrAdmin(BasePermission):
    """Investidor vê os seus dados; admin vê tudo."""
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        from apps.memberships.models import TenantMembership
        try:
            m = TenantMembership.objects.get(user=request.user, is_active=True)
            return m.role in (TenantMembership.ROLE_INVESTIDOR, TenantMembership.ROLE_ADMIN)
        except TenantMembership.DoesNotExist:
            return False
```

---

## Tarefa 2 — ViewSet read-only para investidor

Prompt para `drf-viewset-builder`:
> "Cria `InvestorPortalViewSet` em `apps/contracts/views.py` (ou app dedicada `apps/investors/`). Permission: `IsInvestorOrAdmin`. Lógica: se role=investidor, filtra contratos onde `contract.lead.email == request.user.email` OU FK directa (adicionar `investor_user` nullable a Contract). Action `my_summary`: retorna contagem de unidades por status, total investido (sum payments pagos), próximos pagamentos (due_date ≤ 30 dias). Action `my_documents`: lista PDFs dos contratos."

```python
class InvestorPortalViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsInvestorOrAdmin]
    serializer_class = ContractSerializer

    def get_queryset(self):
        qs = Contract.objects.select_related('unit', 'lead').prefetch_related('payments')
        membership = TenantMembership.objects.get(user=self.request.user, is_active=True)
        if membership.role == TenantMembership.ROLE_INVESTIDOR:
            # Investidor vê apenas os seus contratos
            qs = qs.filter(lead__email=self.request.user.email)
        return qs

    @action(detail=False, methods=['get'])
    def my_summary(self, request):
        """Resumo financeiro do investidor."""
        ...

    @action(detail=False, methods=['get'])
    def my_documents(self, request):
        """Lista de documentos (PDFs) dos contratos."""
        ...
```

---

## Tarefa 3 — Layout de investidor (frontend)

Criar `frontend/src/app/investor/layout.tsx`:
```typescript
// Layout alternativo sem sidebar CRM/Contratos/Obra
// Sidebar simplificada: Dashboard | As Minhas Unidades | Documentos | Perfil
// Verificar role JWT no AuthContext — se role !== 'investidor', redirigir para /
```

Criar `frontend/src/app/investor/page.tsx`:
- Cards: Total Investido (CVE) | Unidades | Próximo Pagamento
- Tabela de contratos com status (DRAFT/ACTIVE/COMPLETED)
- Link para download do PDF de cada contrato (presigned URL S3)

Criar `frontend/src/app/investor/documents/page.tsx`:
- Listagem de todos os documentos dos contratos do investidor
- Filtro por projecto, por estado

---

## Tarefa 4 — Proteger rotas `/investor/` no middleware

**Ler `frontend/src/middleware.ts` antes de editar.**

Adicionar ao middleware:
```typescript
// Rotas /investor/* — apenas investidores e admins
// Verificar cookie refresh_token (já feito pelo middleware base)
// A validação de role acontece no AuthContext + server components
```

Nota: a validação de role real deve acontecer no backend. O middleware Next.js
apenas verifica presença do cookie (sessão activa).

---

## Tarefa 5 — URLs e registos

`apps/investors/urls.py` (ou adicionar a `apps/contracts/urls.py`):
```python
router.register(r'portal', InvestorPortalViewSet, basename='investor-portal')
```

`config/urls.py`:
```python
path('api/v1/investors/', include('apps.investors.urls')),
```

---

## Verificação final

- [ ] `GET /api/v1/investors/portal/` com token de investidor → apenas os seus contratos
- [ ] `GET /api/v1/investors/portal/` com token de outro investidor → 0 resultados (não 403)
- [ ] `GET /api/v1/investors/portal/my_summary/` → totais correctos
- [ ] Admin vê todos os contratos no mesmo endpoint
- [ ] Role `vendedor` → 403
- [ ] `/investor/` no frontend — sidebar sem CRM/Obra
- [ ] `pytest tests/tenant_isolation/test_investor_isolation.py -v`
