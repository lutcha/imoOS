---
name: load-test-celery-queue
description: Locust loadtest com 50 utilizadores concorrentes a disparar mudanças de estado de unidades, medir profundidade da fila de tasks e garantir p95 < 500ms para resposta da API.
argument-hint: "[target_url] [users]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Validar que o sistema aguenta carga realista de vendas simultâneas sem degradação da API ou acumulação de tasks Celery. O teste simula o cenário de lançamento de um projeto com muitos compradores a reservar unidades ao mesmo tempo.

## Code Pattern

```python
# load_tests/locustfile.py
import random
from locust import HttpUser, task, between, events
import redis

REDIS_URL = "redis://localhost:6379/0"
redis_client = redis.from_url(REDIS_URL)


class SalesAgentUser(HttpUser):
    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Autenticar antes dos testes."""
        response = self.client.post("/api/v1/auth/token/", json={
            "email": f"agent_{random.randint(1, 10)}@test.imoos.cv",
            "password": "testpassword123",
        })
        if response.status_code == 200:
            self.token = response.json()["access"]
            self.client.headers.update({"Authorization": f"Bearer {self.token}"})

    @task(3)
    def change_unit_status(self):
        """Simular mudança de estado de unidade — operação mais comum."""
        unit_id = random.randint(1, 100)
        with self.client.patch(
            f"/api/v1/inventory/units/{unit_id}/status/",
            json={"status": "RESERVED", "reason": "Load test reservation"},
            catch_response=True,
        ) as response:
            if response.status_code in [200, 400]:  # 400 = já reservado — válido
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def view_pipeline_kanban(self):
        """Simular carregamento do kanban de vendas."""
        self.client.get("/api/v1/crm/pipeline/kanban/?project_id=1")

    @task(2)
    def create_lead(self):
        """Criar novo lead."""
        self.client.post("/api/v1/crm/leads/", json={
            "full_name": f"Test Lead {random.randint(1000, 9999)}",
            "email": f"lead_{random.randint(1000, 9999)}@test.cv",
            "source": "WALK_IN",
            "project": 1,
        })
```

```python
# load_tests/locustfile.py — monitorização da fila Celery
@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    print("A iniciar monitorização da fila Celery...")


@events.request.add_listener
def on_request(request_type, name, response_time, response_length, **kwargs):
    # Registar p95 manualmente se necessário
    pass


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    # Verificar comprimento da fila após o teste
    queue_length = redis_client.llen("celery")
    high_priority_length = redis_client.llen("high_priority")

    print(f"\n--- Métricas da Fila Celery ---")
    print(f"Fila padrão: {queue_length} tasks pendentes")
    print(f"Fila alta prioridade: {high_priority_length} tasks pendentes")

    if queue_length > 1000:
        print("ALERTA: Fila Celery excede 1000 tasks — possível gargalo!")
    if environment.stats.total.get_response_time_percentile(0.95) > 500:
        print("ALERTA: p95 de resposta API > 500ms — SLA violado!")
```

```bash
# Executar o teste de carga
locust -f load_tests/locustfile.py \
  --host=https://staging.imoos.cv \
  --users=50 \
  --spawn-rate=5 \
  --run-time=5m \
  --headless \
  --html=load_test_report.html
```

## Key Rules

- O critério de aprovação do teste é: p95 < 500ms para endpoints API E fila Celery < 1000 tasks após o teste.
- Usar `--spawn-rate=5` para aumentar gradualmente a carga — não colocar 50 utilizadores de uma vez.
- Monitorizar o Redis com `redis_client.llen("celery")` durante e após o teste.
- Executar o teste de carga antes de cada lançamento de projeto (quando se espera tráfego elevado).

## Anti-Pattern

```python
# ERRADO: correr teste de carga contra produção
# Usar SEMPRE o ambiente de staging — carga em produção afeta clientes reais
host = "https://imoos.cv"  # NUNCA
```
