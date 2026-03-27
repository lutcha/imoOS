# Sprint 8 — Testes de Carga (Pre Go-Live)

## Contexto

Antes do go-live em Cabo Verde, validar que a plataforma aguenta carga real.
Target: **100 utilizadores simultâneos**, **p95 < 500ms**.

Ferramenta: **Locust** (Python, simples de escrever, UI web incluída).

Cenários a testar:
1. **Login flow** (token refresh a cada 15min)
2. **Dashboard** (carregamento de KPIs)
3. **CRM Kanban** (listagem + drag de leads)
4. **Inventário** (listagem + filtros de unidades)
5. **Reserva de unidade** (SELECT FOR UPDATE — critical path)

## Pré-requisitos — Ler antes de começar

```
apps/core/views.py              → health check
apps/crm/views.py               → leads endpoint
apps/inventory/views.py         → units endpoint
config/settings/base.py         → cache, conexões DB
docker-compose.dev.yml          → PostgreSQL config
requirements/development.txt    → adicionar locust
```

## Skills a carregar

```
@.claude/skills/14-testing/load-testing/SKILL.md
@.claude/skills/15-infrastructure/performance-tuning/SKILL.md
```

## Agents a activar

| Agent | Tarefa |
|-------|--------|
| `e2e-test-runner` | Locustfile + relatório de resultados |
| `celery-task-specialist` | Optimizações de query + cache |

---

## Tarefa 1 — Locustfile

Criar `tests/load/locustfile.py`:

```python
"""
Testes de carga ImoOS — Locust
Executar: locust -f tests/load/locustfile.py --host=https://staging.imos.cv
UI: http://localhost:8089
"""
import random
from locust import HttpUser, task, between, events


class ImoOSUser(HttpUser):
    """Simula um utilizador típico da plataforma."""
    wait_time = between(1, 3)
    host = "http://localhost:8001"

    tenant_schema = "demo_promotora"
    access_token = None

    def on_start(self):
        """Login antes de começar os testes."""
        resp = self.client.post(
            "/api/v1/users/auth/token/",
            json={"email": "admin@demo.cv", "password": "ImoOS2026!"},
            headers={"Host": "demo.localhost"},
        )
        if resp.status_code == 200:
            self.access_token = resp.json()["access"]
        else:
            self.environment.runner.quit()

    def auth_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Host": "demo.localhost",
        }

    @task(3)
    def dashboard_stats(self):
        """Dashboard KPIs — endpoint mais chamado."""
        self.client.get("/api/v1/dashboard/stats/", headers=self.auth_headers(),
                       name="/dashboard/stats/")

    @task(2)
    def list_leads(self):
        """Listagem de leads CRM."""
        self.client.get("/api/v1/crm/leads/?page_size=20",
                       headers=self.auth_headers(), name="/crm/leads/")

    @task(2)
    def list_units(self):
        """Listagem do inventário."""
        self.client.get(
            f"/api/v1/inventory/units/?status={random.choice(['AVAILABLE', 'RESERVED', ''])}",
            headers=self.auth_headers(), name="/inventory/units/",
        )

    @task(1)
    def list_projects(self):
        """Listagem de projectos."""
        self.client.get("/api/v1/projects/projects/",
                       headers=self.auth_headers(), name="/projects/projects/")

    @task(1)
    def health_check(self):
        """Health check — deve ser sempre rápido."""
        self.client.get("/api/v1/health/", name="/health/")


class ReservationUser(HttpUser):
    """Simula utilizadores que fazem reservas (carga pesada no DB)."""
    wait_time = between(5, 15)
    host = "http://localhost:8001"
    weight = 3  # 1 reserva para cada 3 utilizadores normais

    access_token = None

    def on_start(self):
        resp = self.client.post(
            "/api/v1/users/auth/token/",
            json={"email": "vendedor@demo.cv", "password": "ImoOS2026!"},
            headers={"Host": "demo.localhost"},
        )
        if resp.status_code == 200:
            self.access_token = resp.json()["access"]

    @task
    def create_reservation(self):
        """Reserva de unidade — SELECT FOR UPDATE."""
        # Listar unidades disponíveis
        resp = self.client.get(
            "/api/v1/inventory/units/?status=AVAILABLE",
            headers={"Authorization": f"Bearer {self.access_token}", "Host": "demo.localhost"},
            name="/inventory/units/ (available)",
        )
        if resp.status_code != 200:
            return
        units = resp.json().get("results", [])
        if not units:
            return

        unit = random.choice(units)
        # Tentar reservar
        self.client.post(
            "/api/v1/crm/reservations/create-reservation/",
            json={
                "unit": unit["id"],
                "lead": None,  # simplificado para load test
                "deposit_amount": 500000,
                "notes": "Load test reservation",
            },
            headers={"Authorization": f"Bearer {self.access_token}", "Host": "demo.localhost"},
            name="/reservations/create-reservation/",
        )
```

---

## Tarefa 2 — Optimizações de performance

Após correr os primeiros testes, identificar os endpoints lentos e optimizar:

### 2a. Índices de base de dados

```python
# apps/crm/models.py — adicionar índices nos campos mais filtrados
class Lead(TenantAwareModel):
    class Meta:
        indexes = [
            models.Index(fields=['pipeline_stage', 'created_at']),
            models.Index(fields=['email']),
        ]

# apps/inventory/models.py
class Unit(TenantAwareModel):
    class Meta:
        indexes = [
            models.Index(fields=['status', 'project']),
            models.Index(fields=['typology', 'status']),
        ]
```

### 2b. Cache do dashboard

```python
# apps/core/views.py — cache de 30s para dashboard stats
from django.core.cache import cache

class DashboardStatsView(APIView):
    def get(self, request):
        schema = connection.schema_name
        cache_key = f"{schema}:dashboard:stats"
        cached = cache.get(cache_key)
        if cached:
            return Response(cached)

        stats = self._compute_stats()
        cache.set(cache_key, stats, timeout=30)
        return Response(stats)
```

### 2c. select_related / prefetch_related

```python
# apps/crm/views.py — evitar N+1 queries
class LeadViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Lead.objects.select_related('assigned_to').prefetch_related(
            'notes', 'reservations',
        ).order_by('-created_at')
```

---

## Tarefa 3 — Relatório de resultados

Após correr `locust --headless --users 100 --spawn-rate 10 --run-time 5m`:

```bash
locust -f tests/load/locustfile.py \
  --host=http://localhost:8001 \
  --headless \
  --users 100 \
  --spawn-rate 10 \
  --run-time 5m \
  --csv=tests/load/results/load_test_$(date +%Y%m%d_%H%M)

# Analisar resultados
python tests/load/analyze_results.py tests/load/results/load_test_*.csv
```

Criar `tests/load/analyze_results.py` que verifica:
- p95 < 500ms em todos os endpoints
- Taxa de erro < 1%
- Throughput > 50 req/s

---

## Verificação final

- [ ] `locust` instalado: `pip install locust`
- [ ] 100 utilizadores simultâneos sem erros (< 1% failure rate)
- [ ] p95 < 500ms em `/dashboard/stats/`
- [ ] p95 < 800ms em `/inventory/units/`
- [ ] `/reservations/create-reservation/` sem deadlocks com 10 concurrent users
- [ ] Relatório CSV gerado em `tests/load/results/`
- [ ] Optimizações documentadas em `docs/performance.md`
