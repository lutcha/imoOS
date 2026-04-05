"""
Views para WhatsApp Business API integration.
Webhooks para receber mensagens e API endpoints para envio.
"""
import logging
import json
from functools import wraps

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.utils.decorators import method_decorator
from django.utils import timezone

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from apps.integrations.models import WhatsAppMessage, NotificationPreference
from apps.integrations.services import WhatsAppClient, NotificationRouter
from apps.users.models import User

logger = logging.getLogger('apps.integrations')


def verify_webhook_signature(request):
    """Verificar assinatura do webhook (Meta ou Twilio)."""
    # Meta verification
    if 'X-Hub-Signature-256' in request.headers:
        # TODO: Implementar verificação HMAC para Meta
        return True
    
    # Twilio verification
    if 'X-Twilio-Signature' in request.headers:
        # TODO: Implementar verificação Twilio
        return True
    
    # Em desenvolvimento, aceitar sem verificação
    if settings.DEBUG:
        return True
    
    return False


@csrf_exempt
@require_http_methods(['GET', 'POST'])
def whatsapp_webhook(request):
    """
    Webhook para receber mensagens e atualizações de status do WhatsApp.
    Suporta Meta e Twilio webhooks.
    
    GET: Verificação do webhook (Meta)
    POST: Recebimento de mensagens
    """
    # Verificação do webhook (Meta)
    if request.method == 'GET':
        mode = request.GET.get('hub.mode')
        token = request.GET.get('hub.verify_token')
        challenge = request.GET.get('hub.challenge')
        
        verify_token = getattr(settings, 'WHATSAPP_VERIFY_TOKEN', 'imoos-webhook-token')
        
        if mode == 'subscribe' and token == verify_token:
            logger.info('Webhook verificado com sucesso')
            return HttpResponse(challenge, content_type='text/plain')
        else:
            logger.warning(f'Falha na verificação do webhook: mode={mode}')
            return HttpResponse('Verification failed', status=403)
    
    # POST - Recebimento de mensagens
    try:
        # Parse do body
        if request.content_type == 'application/json':
            data = json.loads(request.body)
        else:
            # Twilio form data
            data = request.POST.dict()
        
        logger.debug(f'Webhook recebido: {data}')
        
        # Processar com o cliente
        client = WhatsAppClient()
        inbound = client.parse_inbound_message(data)
        
        if not inbound:
            # Pode ser status update
            _process_status_update(data)
            return JsonResponse({'status': 'ok'})
        
        # Buscar utilizador pelo telefone
        user = _find_user_by_phone(inbound.from_phone)
        
        # Criar registro da mensagem recebida
        message = WhatsAppMessage.objects.create(
            user=user,
            direction=WhatsAppMessage.DIRECTION_INBOUND,
            phone_number=inbound.from_phone,
            message_body=inbound.message_body,
            meta_message_id=inbound.message_id,
            status=WhatsAppMessage.STATUS_DELIVERED,
            delivered_at=timezone.now(),
            inbound_response=_extract_response_code(inbound.message_body),
            raw_webhook_data=data
        )
        
        logger.info(f'Mensagem inbound recebida de {inbound.from_phone}: {inbound.message_body[:50]}')
        
        # Processar resposta async
        from apps.integrations.tasks import process_inbound_message
        process_inbound_message.delay(str(message.id))
        
        return JsonResponse({
            'status': 'received',
            'message_id': str(message.id)
        })
        
    except json.JSONDecodeError as e:
        logger.error(f'Erro ao parsear JSON: {e}')
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        logger.exception(f'Erro no webhook: {e}')
        return JsonResponse({'error': 'Internal error'}, status=500)


def _process_status_update(data: dict):
    """Processar atualização de status de mensagem."""
    try:
        # Meta status update
        if 'entry' in data:
            entry = data['entry'][0]
            changes = entry.get('changes', [{}])[0]
            value = changes.get('value', {})
            statuses = value.get('statuses', [])
            
            for status in statuses:
                message_id = status.get('id')
                status_value = status.get('status')  # sent, delivered, read, failed
                
                # Atualizar mensagem no banco
                msg = WhatsAppMessage.objects.filter(meta_message_id=message_id).first()
                if msg:
                    if status_value == 'delivered':
                        msg.mark_delivered()
                    elif status_value == 'read':
                        msg.mark_read()
                    elif status_value == 'failed':
                        error = status.get('errors', [{}])[0]
                        msg.mark_failed(error.get('title', 'Unknown error'))
                    
                    logger.debug(f'Status atualizado: {message_id} -> {status_value}')
    
    except Exception as e:
        logger.error(f'Erro ao processar status update: {e}')


def _find_user_by_phone(phone: str):
    """Buscar utilizador pelo número de telefone."""
    # Normalizar telefone
    phone_clean = phone.replace('+', '').replace(' ', '')
    
    # Tentar match exato
    user = User.objects.filter(phone=phone).first()
    if user:
        return user
    
    # Tentar match sem o +
    user = User.objects.filter(phone=phone_clean).first()
    if user:
        return user
    
    # Tentar match com o +
    if not phone.startswith('+'):
        user = User.objects.filter(phone=f'+{phone}').first()
        if user:
            return user
    
    return None


def _extract_response_code(message_body: str) -> str:
    """Extrair código de resposta rápida da mensagem."""
    body = message_body.strip().upper()
    
    # Emojis específicos
    if body.startswith('✅'):
        return '✅'
    if body.startswith('❌'):
        return '❌'
    if body.startswith('📸') or body.startswith('📷'):
        return '📸'
    
    # Números
    if body in ['1', '2', '3', '4', '5']:
        return body
    
    # Palavras-chave
    keywords = ['CONCLUIDO', 'CONCLUÍDO', 'FEITO', 'DONE', 'OK', 
                'TAREFAS', 'PROGRESSO', 'GESTOR', 'FOTO', 'FOTOS']
    for kw in keywords:
        if kw in body:
            return kw
    
    return body[:50]  # Limitar tamanho


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_test_message(request):
    """
    Endpoint para testar integração WhatsApp.
    
    Body:
        - phone: Número de telefone destino
        - message: Mensagem a enviar (opcional)
        - template: Nome do template (opcional)
    """
    phone = request.data.get('phone')
    message_text = request.data.get('message', 'Teste de integração ImoOS ✅')
    template_name = request.data.get('template')
    
    if not phone:
        return Response(
            {'error': 'Phone number is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        client = WhatsAppClient()
        
        if template_name:
            result = client.send_template_message(
                to_phone=phone,
                template_name=template_name,
                variables=request.data.get('variables', {})
            )
        else:
            result = client.send_free_text(
                to_phone=phone,
                message=message_text
            )
        
        # Registrar no banco
        msg = WhatsAppMessage.objects.create(
            user=request.user,
            direction=WhatsAppMessage.DIRECTION_OUTBOUND,
            phone_number=phone,
            message_body=message_text,
            status=WhatsAppMessage.STATUS_SENT if result.success else WhatsAppMessage.STATUS_FAILED,
            meta_message_id=result.message_id or '',
            error_message=result.error_message or ''
        )
        
        return Response({
            'success': result.success,
            'message_id': str(msg.id),
            'whatsapp_id': result.message_id,
            'error': result.error_message
        })
        
    except Exception as e:
        logger.exception(f'Erro ao enviar mensagem de teste: {e}')
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_task_notification(request):
    """
    Enviar notificação de tarefa para um utilizador.
    
    Body:
        - user_id: ID do utilizador destino
        - task_id: ID da tarefa (opcional)
        - type: Tipo de notificação (assignment, overdue, reminder)
    """
    from apps.construction.models import ConstructionTask
    
    user_id = request.data.get('user_id')
    task_id = request.data.get('task_id')
    notification_type = request.data.get('type', 'assignment')
    
    if not user_id:
        return Response(
            {'error': 'user_id is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(id=user_id)
        task = ConstructionTask.objects.get(id=task_id) if task_id else None
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    except ConstructionTask.DoesNotExist:
        return Response({'error': 'Task not found'}, status=status.HTTP_404_NOT_FOUND)
    
    router = NotificationRouter()
    
    if notification_type == 'assignment':
        if not task:
            return Response({'error': 'task_id required for assignment'}, status=status.HTTP_400_BAD_REQUEST)
        result = router.notify_task_assignment(task)
    elif notification_type == 'overdue':
        if not task:
            return Response({'error': 'task_id required for overdue'}, status=status.HTTP_400_BAD_REQUEST)
        result = router.notify_overdue_task(task)
    elif notification_type == 'reminder':
        if not task:
            return Response({'error': 'task_id required for reminder'}, status=status.HTTP_400_BAD_REQUEST)
        days = request.data.get('days_before', 1)
        result = router.notify_task_reminder(task, days_before=days)
    else:
        return Response({'error': 'Invalid notification type'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(result)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def notification_preferences(request):
    """
    GET: Obter preferências de notificação do utilizador atual.
    PUT: Atualizar preferências.
    """
    preference, created = NotificationPreference.objects.get_or_create(
        user=request.user,
        defaults={
            'whatsapp_enabled': True,
            'email_enabled': True,
            'sms_enabled': False,
        }
    )
    
    if request.method == 'GET':
        return Response({
            'whatsapp_enabled': preference.whatsapp_enabled,
            'email_enabled': preference.email_enabled,
            'sms_enabled': preference.sms_enabled,
            'urgent_only_whatsapp': preference.urgent_only_whatsapp,
            'quiet_hours_start': preference.quiet_hours_start,
            'quiet_hours_end': preference.quiet_hours_end,
            'notify_task_assignment': preference.notify_task_assignment,
            'notify_task_overdue': preference.notify_task_overdue,
            'notify_daily_reminder': preference.notify_daily_reminder,
        })
    
    # PUT - Atualizar
    fields = [
        'whatsapp_enabled', 'email_enabled', 'sms_enabled',
        'urgent_only_whatsapp', 'quiet_hours_start', 'quiet_hours_end',
        'notify_task_assignment', 'notify_task_overdue', 'notify_daily_reminder'
    ]
    
    for field in fields:
        if field in request.data:
            setattr(preference, field, request.data[field])
    
    preference.save()
    
    return Response({'status': 'updated'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_interactive_menu(request):
    """
    Enviar menu interativo WhatsApp para um utilizador.
    
    Body:
        - phone: Número de telefone
        - user_id: ID do utilizador (opcional)
    """
    phone = request.data.get('phone')
    user_id = request.data.get('user_id')
    
    if not phone:
        return Response(
            {'error': 'phone is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    user = None
    if user_id:
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            pass
    
    router = NotificationRouter()
    result = router.send_interactive_task_menu(user or request.user, phone)
    
    return Response(result)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def message_history(request):
    """
    Obter histórico de mensagens do utilizador atual.
    
    Query params:
        - limit: Número máximo de mensagens (default: 50)
        - direction: OUTBOUND, INBOUND ou vazio para ambos
    """
    limit = int(request.query_params.get('limit', 50))
    direction = request.query_params.get('direction')
    
    queryset = WhatsAppMessage.objects.filter(user=request.user)
    
    if direction:
        queryset = queryset.filter(direction=direction)
    
    messages = queryset.order_by('-sent_at')[:limit]
    
    data = [
        {
            'id': str(m.id),
            'direction': m.direction,
            'phone_number': m.phone_number,
            'message_body': m.message_body[:200],
            'status': m.status,
            'sent_at': m.sent_at.isoformat(),
            'delivered_at': m.delivered_at.isoformat() if m.delivered_at else None,
            'read_at': m.read_at.isoformat() if m.read_at else None,
        }
        for m in messages
    ]
    
    return Response({
        'count': len(data),
        'messages': data
    })


class WhatsAppTemplateListView(APIView):
    """
    Listar templates WhatsApp disponíveis.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from apps.integrations.models import WhatsAppTemplate
        
        templates = WhatsAppTemplate.objects.filter(is_active=True)
        
        data = [
            {
                'id': str(t.id),
                'name': t.name,
                'template_type': t.template_type,
                'content_pt': t.content_pt,
                'variables': t.variables,
            }
            for t in templates
        ]
        
        return Response({'templates': data})
