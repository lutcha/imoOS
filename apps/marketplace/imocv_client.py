"""
HTTP client for the imo.cv marketplace API.

Credentials (api_key) come from TenantSettings.imo_cv_api_key — never hardcoded.
BASE_URL comes from settings.IMOCV_API_BASE_URL (env var).
"""
import logging
from decimal import Decimal

import requests
from django.conf import settings

logger = logging.getLogger(__name__)

# Timeout for all imo.cv API calls (seconds)
_REQUEST_TIMEOUT = 15


class ImoCvAPIError(Exception):
    """Raised when imo.cv returns a non-2xx response."""

    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f'imo.cv API error {status_code}: {detail}')


class ImoCvClient:
    """
    Thin wrapper around the imo.cv REST API.

    One instance per tenant — instantiated with the tenant's api_key from
    TenantSettings.imo_cv_api_key. Never share instances across tenants.
    """

    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError('ImoCvClient requires a non-empty api_key')
        self.base_url = settings.IMOCV_API_BASE_URL.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            # Required when calling imo.cv from within Docker network
            'Host': 'localhost',
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _post(self, path: str, payload: dict) -> dict:
        url = f'{self.base_url}{path}'
        try:
            resp = self.session.post(url, json=payload, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.HTTPError as exc:
            raise ImoCvAPIError(exc.response.status_code, exc.response.text) from exc
        except requests.RequestException as exc:
            raise ImoCvAPIError(0, str(exc)) from exc

    def _patch(self, path: str, payload: dict) -> dict:
        url = f'{self.base_url}{path}'
        try:
            resp = self.session.patch(url, json=payload, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
            return resp.json() if resp.content else {}
        except requests.HTTPError as exc:
            raise ImoCvAPIError(exc.response.status_code, exc.response.text) from exc
        except requests.RequestException as exc:
            raise ImoCvAPIError(0, str(exc)) from exc

    def _delete(self, path: str) -> None:
        url = f'{self.base_url}{path}'
        try:
            resp = self.session.delete(url, timeout=_REQUEST_TIMEOUT)
            resp.raise_for_status()
        except requests.HTTPError as exc:
            # 404 on delete is acceptable — listing already removed
            if exc.response.status_code == 404:
                logger.warning('ImoCvClient._delete: listing not found at %s (already removed?)', url)
                return
            raise ImoCvAPIError(exc.response.status_code, exc.response.text) from exc
        except requests.RequestException as exc:
            raise ImoCvAPIError(0, str(exc)) from exc

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def publish_unit(self, unit, price_cve: Decimal) -> dict:
        """
        Publish or update a unit listing on imo.cv.

        If the unit already has an imocv_listing_id, PATCHes the existing listing.
        Otherwise POSTs to create a new one.

        Returns dict with at least {'listing_id': str}.
        """
        payload = self._build_unit_payload(unit, price_cve)

        listing_id = getattr(unit, '_imocv_listing_id', None)
        if listing_id:
            logger.info('ImoCvClient.publish_unit: updating listing %s for unit %s', listing_id, unit.id)
            result = self._patch(f'/api/properties/{listing_id}/', payload)
            return {'listing_id': listing_id, **result}
        else:
            logger.info('ImoCvClient.publish_unit: creating new listing for unit %s', unit.id)
            result = self._post('/api/properties/', payload)
            listing_id = result.get('id') or result.get('listing_id')
            if not listing_id:
                raise ImoCvAPIError(0, 'imo.cv did not return a listing_id in response')
            return {'listing_id': str(listing_id), **result}

    def update_availability(self, imocv_listing_id: str, available: bool) -> None:
        """
        Update availability status without touching price or description data.
        """
        logger.info(
            'ImoCvClient.update_availability: listing=%s available=%s',
            imocv_listing_id, available,
        )
        status_value = 'PUBLICADO' if available else 'PAUSADO'
        self._patch(f'/api/properties/{imocv_listing_id}/', {'status': status_value})

    def remove_listing(self, imocv_listing_id: str) -> None:
        """
        Remove/unpublish a listing from imo.cv. Does not delete the local Unit.
        """
        logger.info('ImoCvClient.remove_listing: listing=%s', imocv_listing_id)
        self._delete(f'/api/properties/{imocv_listing_id}/')

    # ------------------------------------------------------------------
    # Payload builders
    # ------------------------------------------------------------------

    @staticmethod
    def _build_unit_payload(unit, price_cve: Decimal) -> dict:
        """
        Build the JSON payload for the imo.cv /api/properties/ endpoint.

        Field mapping:
          ImoOS Unit          → imo.cv Property
          unit.area_bruta     → area_total
          unit_type.bedrooms  → bedrooms (imo.cv calls this 'rooms' internally)
          unit.status         → status (PUBLICADO / PAUSADO)
        """
        project = unit.floor.building.project
        unit_type = unit.unit_type

        # Map ImoOS unit type code to imo.cv property_type
        type_map = {
            'T0': 'APARTAMENTO', 'T1': 'APARTAMENTO', 'T2': 'APARTAMENTO',
            'T3': 'APARTAMENTO', 'T4': 'APARTAMENTO', 'T5': 'APARTAMENTO',
            'V2': 'MORADIA', 'V3': 'MORADIA', 'V4': 'MORADIA',
            'COMERCIAL': 'COMERCIAL', 'LOJA': 'COMERCIAL',
            'TERRENO': 'TERRENO',
        }
        prop_type = type_map.get(
            (unit_type.code or '').upper(), 'APARTAMENTO'
        )

        # Island/municipality from project address (default Praia/Santiago)
        # imo.cv expects uppercase island codes (e.g. 'SANTIAGO', 'SAO_VICENTE')
        island = (getattr(project, 'island', 'SANTIAGO') or 'SANTIAGO').upper().replace(' ', '_')
        municipality = getattr(project, 'municipality', 'Praia') or 'Praia'
        address = getattr(project, 'address', project.name) or project.name

        payload = {
            'title': f'{unit_type.name} — {project.name} ({unit.code})',
            'description': unit.description or f'{unit_type.name} em {project.name}',
            'listing_type': 'VENDA',
            'property_type': prop_type,
            'status': 'PUBLICADO' if unit.status == 'AVAILABLE' else 'PAUSADO',
            'price': str(price_cve),
            'currency': 'CVE',
            'island': island,
            'municipality': municipality,
            'address': address,
            'area_total': str(unit.area_bruta),
            'bedrooms': unit_type.bedrooms or 0,
            'bathrooms': unit_type.bathrooms or 1,
        }

        if unit.area_util:
            payload['area_util'] = str(unit.area_util)

        # Attach geo location if project has it (required by imo.cv)
        # Uses 'location_geojson_input' — the writable field in imo.cv PropertySerializer
        if hasattr(project, 'location') and project.location:
            try:
                payload['location_geojson_input'] = {
                    'type': 'Point',
                    'coordinates': [project.location.x, project.location.y],
                }
            except Exception:
                pass

        return payload
