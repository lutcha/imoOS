"""
WhatsApp Cloud API client.
Docs: https://developers.facebook.com/docs/whatsapp/cloud-api/

NUNCA hardcodar o token — vem de settings.WHATSAPP_ACCESS_TOKEN (env var).
NUNCA enviar para leads com opt_out=True.
"""
import requests
from django.conf import settings


class WhatsAppCloudClient:
    BASE_URL = 'https://graph.facebook.com/v18.0'

    def __init__(self, phone_number_id: str, access_token: str = None):
        self.phone_number_id = phone_number_id
        self.session = requests.Session()
        # Assumindo a variável de ambiente principal ser partilhada,
        # fallback para TOKEN caso não exista específica, de acordo 
        # com standard config/settings/base.py.
        token = access_token or getattr(settings, 'WHATSAPP_ACCESS_TOKEN', getattr(settings, 'WHATSAPP_API_TOKEN', ''))
        self.session.headers['Authorization'] = f'Bearer {token}'
        self.session.headers['Content-Type'] = 'application/json'

    def send_template(
        self,
        to: str,
        template_name: str,
        language: str,
        components: list[dict],
    ) -> dict:
        """
        Envia template HSM aprovado pela Meta.
        `components`: lista de {type: 'body', parameters: [{type: 'text', text: '...'}]}
        Retorna {messages: [{id: 'wamid...'}]} ou lança requests.HTTPError.
        """
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language},
                'components': components,
            },
        }
        resp = self.session.post(
            f'{self.BASE_URL}/{self.phone_number_id}/messages',
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()

    def send_text(self, to: str, body: str) -> dict:
        """Para mensagens não-template (sessão activa de 24h). Usar com moderação."""
        payload = {
            'messaging_product': 'whatsapp',
            'to': to,
            'type': 'text',
            'text': {'body': body},
        }
        resp = self.session.post(
            f'{self.BASE_URL}/{self.phone_number_id}/messages',
            json=payload,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
