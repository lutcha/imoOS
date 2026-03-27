---
name: api-integration-mock
description: Usar a biblioteca responses para simular chamadas às APIs do imo.cv e bancária em testes. Padrão com decorator @responses.activate, mock de POST /listings e GET /leads.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Isolar os testes de integração de APIs externas usando a biblioteca `responses`. Evita chamadas reais ao imo.cv ou ao banco durante os testes, tornando-os rápidos, deterministas e executáveis offline.

## Code Pattern

```python
# tests/test_marketplace_adapter.py
import responses
import pytest
from decimal import Decimal
from marketplace.services import publish_listing
from inventory.tests.factories import UnitFactory, UnitPricingFactory

@pytest.mark.django_db
class TestListingPublicationAdapter:

    @responses.activate
    def test_publish_listing_success(self, settings):
        settings.IMO_CV_API_URL = "https://api.imo.cv/v1"
        settings.IMO_CV_API_TOKEN = "test-token"

        # Mock do endpoint POST /listings
        responses.add(
            responses.POST,
            "https://api.imo.cv/v1/listings/",
            json={"id": "ext-123", "status": "active"},
            status=201,
        )

        unit = UnitFactory(type="T2", status="AVAILABLE")
        UnitPricingFactory(unit=unit, price_cve=Decimal("5000000"))

        external_id = publish_listing(unit)

        assert external_id == "ext-123"
        assert unit.external_listing_id == "ext-123"
        assert len(responses.calls) == 1
        assert responses.calls[0].request.headers["Authorization"] == "Bearer test-token"

    @responses.activate
    def test_publish_listing_api_error_raises(self, settings):
        settings.IMO_CV_API_URL = "https://api.imo.cv/v1"
        responses.add(
            responses.POST,
            "https://api.imo.cv/v1/listings/",
            json={"error": "Unauthorized"},
            status=401,
        )

        unit = UnitFactory()
        with pytest.raises(Exception):  # requests.HTTPError
            publish_listing(unit)
```

```python
# tests/test_lead_webhook.py
import responses
import pytest

@pytest.mark.django_db
class TestImoCvLeadWebhook:

    @responses.activate
    def test_get_leads_from_imo_cv(self, settings, api_client):
        settings.IMO_CV_API_URL = "https://api.imo.cv/v1"

        # Mock de GET /leads
        responses.add(
            responses.GET,
            "https://api.imo.cv/v1/leads/",
            json={
                "results": [
                    {"id": "lead-1", "name": "João Silva", "phone": "+238912345", "listing_id": "ext-123"},
                ],
                "count": 1,
            },
            status=200,
        )

        from marketplace.services import fetch_leads_from_marketplace
        leads = fetch_leads_from_marketplace()

        assert len(leads) == 1
        assert leads[0]["name"] == "João Silva"
```

```python
# conftest.py — fixtures reutilizáveis
import pytest
import responses as responses_lib

@pytest.fixture
def mock_imo_cv_api(settings):
    settings.IMO_CV_API_URL = "https://api.imo.cv/v1"
    settings.IMO_CV_API_TOKEN = "test-token"

    with responses_lib.RequestsMock() as rsps:
        yield rsps
```

## Key Rules

- Usar `@responses.activate` ou `responses.RequestsMock()` como context manager — nunca deixar requests reais em testes.
- Verificar `responses.calls` para confirmar que a API foi chamada com os parâmetros corretos (headers, body).
- Testar sempre os cenários de erro (401, 500, timeout) além do caminho feliz.
- Usar `pytest-django` com `@pytest.mark.django_db` em todos os testes que acedem à base de dados.

## Anti-Pattern

```python
# ERRADO: usar unittest.mock.patch para simular requests — mais frágil e verboso
@patch("requests.post")
def test_publish(self, mock_post):
    mock_post.return_value.json.return_value = {"id": "ext-123"}
    mock_post.return_value.status_code = 201
    # Não verifica URL, headers, nem outros detalhes do pedido
```
