"""
Testes de carga ImoOS — Locust
===============================
Alvo: 100 utilizadores simultâneos, p95 < 500ms

Executar (UI web em http://localhost:8089):
    locust -f tests/load/locustfile.py --host=http://localhost:8001

Executar headless (gera CSV de resultados):
    locust -f tests/load/locustfile.py \\
      --host=http://localhost:8001 \\
      --headless --users 100 --spawn-rate 10 --run-time 5m \\
      --csv=tests/load/results/load_test_$(date +%Y%m%d_%H%M)

Analisar:
    python tests/load/analyze_results.py tests/load/results/load_test_*.csv
"""
import random

from locust import HttpUser, between, events, task

# ---------------------------------------------------------------------------
# Configuração por ambiente — sobrepor via --host ou variável de ambiente
# ---------------------------------------------------------------------------
HOST = "http://localhost:8001"
TENANT_HOST_HEADER = "demo.localhost"

ADMIN_CREDENTIALS = {"email": "admin@demo.cv", "password": "ImoOS2026!"}
SELLER_CREDENTIALS = {"email": "vendedor@demo.cv", "password": "ImoOS2026!"}


# ---------------------------------------------------------------------------
# Utilizador típico: dashboard + CRM + inventário
# ---------------------------------------------------------------------------
class ImoOSUser(HttpUser):
    """Simula um gestor/comercial típico da plataforma."""

    wait_time = between(1, 3)
    host = HOST

    access_token: str | None = None

    def on_start(self):
        """Login antes de começar os testes — falha rápida se o server não responde."""
        resp = self.client.post(
            "/api/v1/users/auth/token/",
            json=ADMIN_CREDENTIALS,
            headers={"Host": TENANT_HOST_HEADER},
            name="/auth/token/ [login]",
        )
        if resp.status_code == 200:
            self.access_token = resp.json()["access"]
        else:
            # Server não responde correctamente — abort runner
            self.environment.runner.quit()

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Host": TENANT_HOST_HEADER,
        }

    # weight=3 → dashboard é o endpoint mais chamado
    @task(3)
    def dashboard_stats(self):
        self.client.get(
            "/api/v1/dashboard/stats/",
            headers=self._headers(),
            name="/dashboard/stats/",
        )

    @task(2)
    def list_leads(self):
        self.client.get(
            "/api/v1/crm/leads/?page_size=20",
            headers=self._headers(),
            name="/crm/leads/",
        )

    @task(2)
    def crm_pipeline(self):
        """Kanban board — leads agrupados por stage."""
        self.client.get(
            "/api/v1/crm/leads/pipeline/",
            headers=self._headers(),
            name="/crm/leads/pipeline/",
        )

    @task(2)
    def list_units(self):
        status = random.choice(["AVAILABLE", "RESERVED", ""])
        url = f"/api/v1/inventory/units/?page_size=20"
        if status:
            url += f"&status={status}"
        self.client.get(url, headers=self._headers(), name="/inventory/units/")

    @task(1)
    def list_projects(self):
        self.client.get(
            "/api/v1/projects/projects/",
            headers=self._headers(),
            name="/projects/projects/",
        )

    @task(1)
    def health_check(self):
        """Deve ser sempre sub-10ms — alerta se for mais lento."""
        self.client.get("/api/v1/health/", name="/health/")


# ---------------------------------------------------------------------------
# Utilizador de reservas: SELECT FOR UPDATE — critical path
# ---------------------------------------------------------------------------
class ReservationUser(HttpUser):
    """Simula comerciais a reservar unidades (carga pesada no DB)."""

    wait_time = between(5, 15)
    host = HOST
    weight = 3  # ratio: 1 reservation user por cada 3 normal users

    access_token: str | None = None

    def on_start(self):
        resp = self.client.post(
            "/api/v1/users/auth/token/",
            json=SELLER_CREDENTIALS,
            headers={"Host": TENANT_HOST_HEADER},
            name="/auth/token/ [seller login]",
        )
        if resp.status_code == 200:
            self.access_token = resp.json()["access"]

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Host": TENANT_HOST_HEADER,
        }

    @task
    def reserve_unit(self):
        """Fluxo completo: listar disponíveis → reservar uma aleatória."""
        if not self.access_token:
            return

        # 1. Listar unidades disponíveis
        resp = self.client.get(
            "/api/v1/inventory/units/?status=AVAILABLE&page_size=50",
            headers=self._headers(),
            name="/inventory/units/ [available]",
        )
        if resp.status_code != 200:
            return

        units = resp.json().get("results", [])
        if not units:
            return

        unit = random.choice(units)

        # 2. Criar reserva (SELECT FOR UPDATE inside create_reservation service)
        self.client.post(
            "/api/v1/crm/reservations/create-reservation/",
            json={
                "unit": unit["id"],
                "lead": None,
                "deposit_amount": 500000,
                "notes": "Load test reservation",
            },
            headers=self._headers(),
            name="/reservations/create-reservation/",
        )


# ---------------------------------------------------------------------------
# Event hooks — print summary thresholds to console at test end
# ---------------------------------------------------------------------------
@events.quitting.add_listener
def on_quit(environment, **kwargs):
    """Avalia p95 e failure rate ao terminar — exit 1 se falharem."""
    stats = environment.runner.stats
    failures = stats.total.fail_ratio
    p95 = stats.total.get_response_time_percentile(0.95)

    print("\n" + "=" * 60)
    print("ImoOS Load Test — Relatório Final")
    print("=" * 60)
    print(f"  Requests totais : {stats.total.num_requests}")
    print(f"  Failure rate    : {failures:.2%}  (alvo < 1%)")
    print(f"  p95 global      : {p95:.0f}ms    (alvo < 500ms)")
    print("=" * 60)

    if failures > 0.01:
        print("❌ FALHA: Taxa de erro acima de 1%")
        environment.process_exit_code = 1
    elif p95 > 500:
        print("❌ FALHA: p95 acima de 500ms")
        environment.process_exit_code = 1
    else:
        print("✅ PASSOU: todos os targets cumpridos")
