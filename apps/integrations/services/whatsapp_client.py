"""
Cliente WhatsApp Business API usando Twilio ou Meta API direta.
Suporta envio de templates, texto livre e processamento de webhooks.
"""
import logging
import json
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from datetime import datetime

import requests
from django.conf import settings

logger = logging.getLogger('apps.integrations')


class WhatsAppClientError(Exception):
    """Erro específico do cliente WhatsApp."""
    pass


@dataclass
class MessageResponse:
    """Resposta padronizada de envio de mensagem."""
    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    raw_response: Optional[Dict] = None


@dataclass
class InboundMessage:
    """Mensagem recebida parseada do webhook."""
    from_phone: str
    message_body: str
    timestamp: datetime
    message_id: str
    profile_name: Optional[str] = None
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class WhatsAppClient:
    """
    Cliente para WhatsApp Business API.
    Suporta Twilio e Meta API direta (configurável via settings).
    """

    PROVIDER_TWILIO = 'twilio'
    PROVIDER_META = 'meta'

    def __init__(self, provider: Optional[str] = None):
        """
        Inicializar cliente com provider específico.
        
        Args:
            provider: 'twilio' ou 'meta'. Se None, usa WHATSAPP_PROVIDER das settings.
        """
        self.provider = provider or getattr(settings, 'WHATSAPP_PROVIDER', self.PROVIDER_TWILIO)
        
        # Twilio config
        self.twilio_account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '')
        self.twilio_auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '')
        self.twilio_whatsapp_number = getattr(settings, 'TWILIO_WHATSAPP_NUMBER', '')
        
        # Meta config
        self.meta_phone_number_id = getattr(settings, 'WHATSAPP_PHONE_NUMBER_ID', '')
        self.meta_access_token = getattr(settings, 'WHATSAPP_ACCESS_TOKEN', '')
        self.meta_api_version = getattr(settings, 'WHATSAPP_API_VERSION', 'v18.0')
        
        self._validate_config()

    def _validate_config(self):
        """Validar configuração do provider ativo."""
        if self.provider == self.PROVIDER_TWILIO:
            if not all([self.twilio_account_sid, self.twilio_auth_token, self.twilio_whatsapp_number]):
                logger.warning('Twilio config incompleta - modo de simulação ativo')
        elif self.provider == self.PROVIDER_META:
            if not all([self.meta_phone_number_id, self.meta_access_token]):
                logger.warning('Meta API config incompleta - modo de simulação ativo')

    def _format_phone(self, phone: str) -> str:
        """Formatar número de telefone para padrão internacional."""
        # Remover espaços e caracteres não numéricos exceto +
        cleaned = ''.join(c for c in phone if c.isdigit() or c == '+')
        # Garantir prefixo +
        if not cleaned.startswith('+'):
            # Assumir Cabo Verde (+238) se não tiver código do país
            cleaned = '+238' + cleaned
        return cleaned

    def send_template_message(
        self,
        to_phone: str,
        template_name: str,
        variables: Dict[str, str],
        language: str = 'pt_PT'
    ) -> MessageResponse:
        """
        Enviar mensagem template aprovada pela Meta.
        
        Args:
            to_phone: Número do destinatário (+2389991234)
            template_name: Nome do template registrado
            variables: Dict com variáveis para substituição {'nome': 'João'}
            language: Código do idioma (pt_PT, pt_BR)
        
        Returns:
            MessageResponse com resultado do envio
        """
        phone = self._format_phone(to_phone)
        
        try:
            if self.provider == self.PROVIDER_TWILIO:
                return self._send_template_twilio(phone, template_name, variables)
            else:
                return self._send_template_meta(phone, template_name, variables, language)
        except Exception as e:
            logger.error(f'Erro ao enviar template WhatsApp: {e}')
            return MessageResponse(success=False, error_message=str(e))

    def _send_template_twilio(
        self,
        to_phone: str,
        template_name: str,
        variables: Dict[str, str]
    ) -> MessageResponse:
        """Enviar template via Twilio API."""
        from twilio.rest import Client
        
        try:
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Construir parâmetros do template
            params = list(variables.values())
            
            message = client.messages.create(
                from_=f'whatsapp:{self.twilio_whatsapp_number}',
                to=f'whatsapp:{to_phone}',
                content_sid=template_name if template_name.startswith('HX') else None,
                content_variables=json.dumps(variables) if variables else None,
                body=None if template_name.startswith('HX') else f'Template: {template_name}'
            )
            
            logger.info(f'Mensagem Twilio enviada: {message.sid}')
            return MessageResponse(
                success=True,
                message_id=message.sid,
                raw_response={'sid': message.sid, 'status': message.status}
            )
        except Exception as e:
            logger.error(f'Erro Twilio: {e}')
            return MessageResponse(success=False, error_message=str(e))

    def _send_template_meta(
        self,
        to_phone: str,
        template_name: str,
        variables: Dict[str, str],
        language: str
    ) -> MessageResponse:
        """Enviar template via Meta WhatsApp Business API."""
        url = f'https://graph.facebook.com/{self.meta_api_version}/{self.meta_phone_number_id}/messages'
        
        # Construir componentes de parâmetros
        template_params = []
        for key, value in variables.items():
            template_params.append({
                'type': 'text',
                'text': str(value)
            })
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to_phone,
            'type': 'template',
            'template': {
                'name': template_name,
                'language': {'code': language},
                'components': [
                    {
                        'type': 'body',
                        'parameters': template_params
                    }
                ] if template_params else None
            }
        }
        
        # Remover components se vazio
        if not template_params:
            del payload['template']['components']
        
        headers = {
            'Authorization': f'Bearer {self.meta_access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            message_id = data.get('messages', [{}])[0].get('id')
            logger.info(f'Mensagem Meta enviada: {message_id}')
            
            return MessageResponse(
                success=True,
                message_id=message_id,
                raw_response=data
            )
        except requests.exceptions.RequestException as e:
            logger.error(f'Erro Meta API: {e}')
            error_msg = str(e)
            if hasattr(e.response, 'text'):
                error_msg += f' - {e.response.text}'
            return MessageResponse(success=False, error_message=error_msg)

    def send_free_text(
        self,
        to_phone: str,
        message: str,
        preview_url: bool = False
    ) -> MessageResponse:
        """
        Enviar texto livre (apenas dentro da janela de 24h da conversa).
        
        Args:
            to_phone: Número do destinatário
            message: Conteúdo da mensagem
            preview_url: Se deve gerar preview de links
        """
        phone = self._format_phone(to_phone)
        
        try:
            if self.provider == self.PROVIDER_TWILIO:
                return self._send_text_twilio(phone, message)
            else:
                return self._send_text_meta(phone, message, preview_url)
        except Exception as e:
            logger.error(f'Erro ao enviar texto WhatsApp: {e}')
            return MessageResponse(success=False, error_message=str(e))

    def _send_text_twilio(self, to_phone: str, message: str) -> MessageResponse:
        """Enviar texto via Twilio."""
        from twilio.rest import Client
        
        client = Client(self.twilio_account_sid, self.twilio_auth_token)
        
        twilio_message = client.messages.create(
            from_=f'whatsapp:{self.twilio_whatsapp_number}',
            to=f'whatsapp:{to_phone}',
            body=message
        )
        
        return MessageResponse(
            success=True,
            message_id=twilio_message.sid,
            raw_response={'sid': twilio_message.sid}
        )

    def _send_text_meta(
        self,
        to_phone: str,
        message: str,
        preview_url: bool
    ) -> MessageResponse:
        """Enviar texto via Meta API."""
        url = f'https://graph.facebook.com/{self.meta_api_version}/{self.meta_phone_number_id}/messages'
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': to_phone,
            'type': 'text',
            'text': {
                'body': message,
                'preview_url': preview_url
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.meta_access_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        message_id = data.get('messages', [{}])[0].get('id')
        
        return MessageResponse(
            success=True,
            message_id=message_id,
            raw_response=data
        )

    def send_interactive_menu(
        self,
        to_phone: str,
        header: str,
        body: str,
        footer: str,
        buttons: List[Dict[str, str]]
    ) -> MessageResponse:
        """
        Enviar menu interativo com botões.
        
        Args:
            to_phone: Número do destinatário
            header: Título do menu
            body: Texto principal
            footer: Texto de rodapé
            buttons: Lista de dicts [{'id': '1', 'title': 'Ver tarefas'}, ...]
        """
        phone = self._format_phone(to_phone)
        
        if self.provider == self.PROVIDER_TWILIO:
            # Twilio não suporta botões interativos diretamente
            # Fallback para texto com opções numeradas
            text = f"*{header}*\n\n{body}\n\n"
            for btn in buttons:
                text += f"{btn['id']}. {btn['title']}\n"
            text += f"\n_{footer}_"
            return self.send_free_text(phone, text)
        
        # Meta API com botões interativos
        url = f'https://graph.facebook.com/{self.meta_api_version}/{self.meta_phone_number_id}/messages'
        
        action_buttons = [
            {
                'type': 'reply',
                'reply': {
                    'id': btn['id'],
                    'title': btn['title'][:20]  # Máximo 20 caracteres
                }
            }
            for btn in buttons[:3]  # Máximo 3 botões
        ]
        
        payload = {
            'messaging_product': 'whatsapp',
            'recipient_type': 'individual',
            'to': phone,
            'type': 'interactive',
            'interactive': {
                'type': 'button',
                'header': {
                    'type': 'text',
                    'text': header[:60]  # Máximo 60 caracteres
                },
                'body': {
                    'text': body[:1024]  # Máximo 1024 caracteres
                },
                'footer': {
                    'text': footer[:60]  # Máximo 60 caracteres
                },
                'action': {
                    'buttons': action_buttons
                }
            }
        }
        
        headers = {
            'Authorization': f'Bearer {self.meta_access_token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            message_id = data.get('messages', [{}])[0].get('id')
            
            return MessageResponse(
                success=True,
                message_id=message_id,
                raw_response=data
            )
        except requests.exceptions.RequestException as e:
            logger.error(f'Erro ao enviar menu interativo: {e}')
            return MessageResponse(success=False, error_message=str(e))

    def parse_inbound_message(self, webhook_data: Dict[str, Any]) -> Optional[InboundMessage]:
        """
        Parse de webhook da Meta ou Twilio para formato padronizado.
        
        Args:
            webhook_data: Dados brutos do webhook
        
        Returns:
            InboundMessage parseada ou None se inválido
        """
        try:
            # Detectar tipo de webhook
            if 'entry' in webhook_data:
                # Meta webhook
                return self._parse_meta_webhook(webhook_data)
            elif 'Body' in webhook_data or 'From' in webhook_data:
                # Twilio webhook
                return self._parse_twilio_webhook(webhook_data)
            else:
                logger.warning(f'Formato de webhook desconhecido: {webhook_data.keys()}')
                return None
        except Exception as e:
            logger.error(f'Erro ao parsear webhook: {e}')
            return None

    def _parse_meta_webhook(self, data: Dict) -> Optional[InboundMessage]:
        """Parse de webhook da Meta."""
        try:
            entry = data.get('entry', [{}])[0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            messages = value.get('messages', [])
            
            if not messages:
                return None
            
            message = messages[0]
            contacts = value.get('contacts', [{}])[0]
            
            from_phone = message.get('from', '')
            message_id = message.get('id', '')
            timestamp = datetime.fromtimestamp(int(message.get('timestamp', 0)))
            profile_name = contacts.get('profile', {}).get('name')
            
            # Extrair conteúdo da mensagem
            msg_type = message.get('type', 'text')
            if msg_type == 'text':
                message_body = message.get('text', {}).get('body', '')
            elif msg_type == 'interactive':
                # Botão clicado
                interactive = message.get('interactive', {})
                if 'button_reply' in interactive:
                    message_body = interactive['button_reply'].get('id', '')
                elif 'list_reply' in interactive:
                    message_body = interactive['list_reply'].get('id', '')
                else:
                    message_body = ''
            elif msg_type == 'button':
                message_body = message.get('button', {}).get('text', '')
            else:
                message_body = f'[{msg_type}]'
            
            return InboundMessage(
                from_phone=from_phone,
                message_body=message_body,
                timestamp=timestamp,
                message_id=message_id,
                profile_name=profile_name
            )
        except Exception as e:
            logger.error(f'Erro ao parsear Meta webhook: {e}')
            return None

    def _parse_twilio_webhook(self, data: Dict) -> Optional[InboundMessage]:
        """Parse de webhook da Twilio."""
        try:
            from_phone = data.get('From', '').replace('whatsapp:', '')
            message_body = data.get('Body', '')
            message_id = data.get('MessageSid', '')
            profile_name = data.get('ProfileName')
            
            # Twilio não envia timestamp no webhook
            timestamp = datetime.now()
            
            return InboundMessage(
                from_phone=from_phone,
                message_body=message_body,
                timestamp=timestamp,
                message_id=message_id,
                profile_name=profile_name
            )
        except Exception as e:
            logger.error(f'Erro ao parsear Twilio webhook: {e}')
            return None

    def get_message_status(self, message_id: str) -> Dict[str, Any]:
        """
        Consultar status de uma mensagem enviada.
        
        Args:
            message_id: ID da mensagem na Meta/Twilio
        
        Returns:
            Dict com status e metadados
        """
        # Implementação específica por provider
        if self.provider == self.PROVIDER_TWILIO:
            from twilio.rest import Client
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            try:
                message = client.messages(message_id).fetch()
                return {
                    'status': message.status,
                    'delivered_at': message.date_sent.isoformat() if message.date_sent else None,
                    'error_message': message.error_message
                }
            except Exception as e:
                return {'status': 'unknown', 'error': str(e)}
        
        # Meta API não tem endpoint direto para consulta de status
        return {'status': 'unknown', 'note': 'Use webhooks para atualizações de status'}
