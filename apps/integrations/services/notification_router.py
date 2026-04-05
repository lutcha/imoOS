"""
Notification Router - Decide o canal de notificação baseado em preferências e urgência.
Integra com ConstructionTask, User, Lead models existentes.
"""
import logging
from typing import Optional, List
from datetime import date

from django.db import transaction
from django.utils import timezone

from apps.integrations.models import (
    WhatsAppMessage, WhatsAppTemplate, NotificationPreference
)
from apps.integrations.services.whatsapp_client import WhatsAppClient, MessageResponse

logger = logging.getLogger('apps.integrations')


class NotificationRouter:
    """
    Roteador de notificações que decide entre WhatsApp, Email, SMS baseado em:
    - Preferências do utilizador
    - Urgência da notificação
    - Disponibilidade dos serviços
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Inicializar router com cliente WhatsApp.
        
        Args:
            provider: 'twilio', 'meta' ou None para usar default
        """
        self.whatsapp_client = WhatsAppClient(provider=provider)

    def _get_or_create_preference(self, user) -> NotificationPreference:
        """Obter ou criar preferências de notificação para um utilizador."""
        from apps.integrations.models import NotificationPreference
        
        preference, created = NotificationPreference.objects.get_or_create(
            user=user,
            defaults={
                'whatsapp_enabled': True,
                'email_enabled': True,
                'sms_enabled': False,
                'urgent_only_whatsapp': False,
            }
        )
        return preference

    def _log_message(
        self,
        phone: str,
        body: str,
        direction: str = WhatsAppMessage.DIRECTION_OUTBOUND,
        user=None,
        lead=None,
        task=None,
        template=None,
        status: str = WhatsAppMessage.STATUS_SENT,
        meta_message_id: str = '',
        error_message: str = ''
    ) -> WhatsAppMessage:
        """Criar registro de mensagem no banco de dados."""
        return WhatsAppMessage.objects.create(
            user=user,
            lead=lead,
            task=task,
            template=template,
            direction=direction,
            phone_number=phone,
            message_body=body,
            status=status,
            meta_message_id=meta_message_id,
            error_message=error_message
        )

    def _get_user_phone(self, user) -> Optional[str]:
        """Extrair número de telefone do utilizador."""
        # Tentar campo phone do User
        phone = getattr(user, 'phone', None)
        if phone:
            return phone
        
        # Fallback: tentar perfil se existir
        if hasattr(user, 'profile'):
            phone = getattr(user.profile, 'phone', None)
            if phone:
                return phone
        
        return None

    def send_whatsapp_or_email(
        self,
        user,
        subject: str,
        message: str,
        whatsapp_template_name: Optional[str] = None,
        template_variables: Optional[dict] = None,
        is_urgent: bool = False,
        related_task=None
    ) -> dict:
        """
        Enviar notificação via WhatsApp ou Email baseado nas preferências.
        
        Args:
            user: User instance
            subject: Assunto (para email)
            message: Mensagem completa (para email ou texto livre WhatsApp)
            whatsapp_template_name: Nome do template WhatsApp (opcional)
            template_variables: Variáveis para o template
            is_urgent: Se é notificação urgente
            related_task: ConstructionTask relacionada (opcional)
        
        Returns:
            Dict com resultado do envio
        """
        preference = self._get_or_create_preference(user)
        
        # Tentar WhatsApp primeiro se habilitado
        if preference.should_notify_whatsapp(is_urgent=is_urgent):
            phone = self._get_user_phone(user)
            if phone:
                result = self._send_whatsapp_notification(
                    phone=phone,
                    user=user,
                    template_name=whatsapp_template_name,
                    template_variables=template_variables or {},
                    free_text=message,
                    related_task=related_task
                )
                if result['success']:
                    return result
                # Se falhou, tentar email
                logger.warning(f'WhatsApp falhou para {user.email}, tentando email')
        
        # Fallback para email
        if preference.email_enabled:
            return self._send_email_notification(user, subject, message, related_task)
        
        # Nenhum canal disponível
        return {
            'success': False,
            'channel': 'none',
            'error': 'Nenhum canal de notificação habilitado'
        }

    def _send_whatsapp_notification(
        self,
        phone: str,
        user,
        template_name: Optional[str],
        template_variables: dict,
        free_text: str,
        related_task=None
    ) -> dict:
        """Enviar notificação WhatsApp."""
        try:
            # Se tem template, usar template
            if template_name:
                template = WhatsAppTemplate.objects.filter(
                    name=template_name,
                    is_active=True
                ).first()
                
                if template:
                    response = self.whatsapp_client.send_template_message(
                        to_phone=phone,
                        template_name=template.meta_template_id or template_name,
                        variables=template_variables,
                        language=template.language
                    )
                    
                    message = self._log_message(
                        phone=phone,
                        body=template.content_pt,
                        user=user,
                        task=related_task,
                        template=template,
                        status=WhatsAppMessage.STATUS_SENT if response.success else WhatsAppMessage.STATUS_FAILED,
                        meta_message_id=response.message_id or '',
                        error_message=response.error_message or ''
                    )
                    
                    return {
                        'success': response.success,
                        'channel': 'whatsapp',
                        'message_id': message.id,
                        'whatsapp_id': response.message_id,
                        'error': response.error_message
                    }
            
            # Fallback para texto livre
            response = self.whatsapp_client.send_free_text(
                to_phone=phone,
                message=free_text
            )
            
            message = self._log_message(
                phone=phone,
                body=free_text[:500],  # Limitar tamanho
                user=user,
                task=related_task,
                status=WhatsAppMessage.STATUS_SENT if response.success else WhatsAppMessage.STATUS_FAILED,
                meta_message_id=response.message_id or '',
                error_message=response.error_message or ''
            )
            
            return {
                'success': response.success,
                'channel': 'whatsapp',
                'message_id': message.id,
                'whatsapp_id': response.message_id,
                'error': response.error_message
            }
            
        except Exception as e:
            logger.error(f'Erro ao enviar WhatsApp: {e}')
            return {'success': False, 'channel': 'whatsapp', 'error': str(e)}

    def _send_email_notification(self, user, subject: str, message: str, related_task=None) -> dict:
        """Enviar notificação por email."""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False
            )
            
            return {
                'success': True,
                'channel': 'email',
                'recipient': user.email
            }
        except Exception as e:
            logger.error(f'Erro ao enviar email: {e}')
            return {'success': False, 'channel': 'email', 'error': str(e)}

    # ==================== Notificações Específicas ====================

    def notify_task_assignment(self, task) -> dict:
        """
        Notificar encarregado da nova tarefa.
        
        Args:
            task: ConstructionTask instance
        """
        if not task.assigned_to:
            logger.warning(f'Tarefa {task.id} não tem assignee')
            return {'success': False, 'error': 'Tarefa não tem responsável'}
        
        user = task.assigned_to
        
        subject = f'Nova Tarefa: {task.name}'
        message = (
            f'Olá {user.first_name or user.email},\n\n'
            f'Foi-lhe atribuída uma nova tarefa:\n'
            f'*Tarefa:* {task.name}\n'
            f'*Data limite:* {task.due_date}\n'
            f'*Status:* {task.get_status_display()}\n\n'
            f'Para mais detalhes, aceda à plataforma ImoOS.'
        )
        
        return self.send_whatsapp_or_email(
            user=user,
            subject=subject,
            message=message,
            whatsapp_template_name='task_reminder',
            template_variables={
                'nome': user.first_name or 'Utilizador',
                'tarefa': task.name,
                'data': str(task.due_date)
            },
            is_urgent=False,
            related_task=task
        )

    def notify_overdue_task(self, task) -> dict:
        """
        Alerta de atraso - sempre WhatsApp se disponível.
        
        Args:
            task: ConstructionTask instance
        """
        if not task.assigned_to:
            return {'success': False, 'error': 'Tarefa não tem responsável'}
        
        user = task.assigned_to
        days_overdue = (timezone.now().date() - task.due_date).days
        
        subject = f'⚠️ TAREFA ATRASADA: {task.name}'
        message = (
            f'⚠️ *ALERTA DE ATRASO* ⚠️\n\n'
            f'A tarefa *{task.name}* está atrasada há *{days_overdue} dias*.\n'
            f'Data limite: {task.due_date}\n\n'
            f'Por favor, atualize o status ou contacte o gestor.'
        )
        
        # Enviar WhatsApp + Email para urgentes
        result = self.send_whatsapp_or_email(
            user=user,
            subject=subject,
            message=message,
            whatsapp_template_name='overdue_alert',
            template_variables={
                'nome': user.first_name or 'Utilizador',
                'tarefa': task.name,
                'dias': str(days_overdue)
            },
            is_urgent=True,
            related_task=task
        )
        
        # Se WhatsApp sucesso, também enviar email para garantir
        if result['channel'] == 'whatsapp' and result['success']:
            email_result = self._send_email_notification(user, subject, message, task)
            result['email_also_sent'] = email_result['success']
        
        return result

    def notify_task_reminder(self, task, days_before: int = 1) -> dict:
        """
        Lembrete de tarefa próxima do vencimento.
        
        Args:
            task: ConstructionTask instance
            days_before: Dias antes do vencimento para enviar lembrete
        """
        if not task.assigned_to:
            return {'success': False, 'error': 'Tarefa não tem responsável'}
        
        user = task.assigned_to
        
        subject = f'Lembrete: {task.name} vence em breve'
        message = (
            f'🔔 *Lembrete de Tarefa* 🔔\n\n'
            f'A tarefa *{task.name}* vence em {days_before} dia(s).\n'
            f'Data limite: {task.due_date}\n\n'
            f'_Responda ✅ para marcar como concluída_'
        )
        
        return self.send_whatsapp_or_email(
            user=user,
            subject=subject,
            message=message,
            whatsapp_template_name='task_reminder',
            template_variables={
                'nome': user.first_name or 'Utilizador',
                'tarefa': task.name,
                'data': str(task.due_date)
            },
            is_urgent=False,
            related_task=task
        )

    def notify_daily_report_reminder(self, user, project_name: str) -> dict:
        """
        Lembrete para enviar relatório diário de obra.
        
        Args:
            user: User instance
            project_name: Nome do projeto
        """
        subject = f'Lembrete: Relatório Diário - {project_name}'
        message = (
            f'📋 *Relatório Diário de Obra* 📋\n\n'
            f'Não se esqueça de enviar o relatório diário do projeto *{project_name}*.\n\n'
            f'_Responda 📸 para enviar fotos diretamente_'
        )
        
        return self.send_whatsapp_or_email(
            user=user,
            subject=subject,
            message=message,
            whatsapp_template_name='daily_report_reminder',
            template_variables={
                'nome': user.first_name or 'Utilizador',
                'projeto': project_name
            },
            is_urgent=False
        )

    def send_interactive_task_menu(self, user, phone: str) -> dict:
        """
        Enviar menu interativo para gestão de tarefas.
        
        Args:
            user: User instance
            phone: Número de telefone
        """
        try:
            response = self.whatsapp_client.send_interactive_menu(
                to_phone=phone,
                header='🏗️ ImoOS Obra',
                body=(
                    f'Olá {user.first_name or "Utilizador"}!\n\n'
                    'O que deseja fazer?'
                ),
                footer='Selecione uma opção abaixo',
                buttons=[
                    {'id': '1', 'title': 'Ver tarefas'},
                    {'id': '2', 'title': 'Atualizar progresso'},
                    {'id': '3', 'title': 'Falar com gestor'},
                ]
            )
            
            if response.success:
                self._log_message(
                    phone=phone,
                    body='Menu interativo: Ver tarefas / Atualizar progresso / Falar com gestor',
                    user=user,
                    status=WhatsAppMessage.STATUS_SENT,
                    meta_message_id=response.message_id or ''
                )
            
            return {
                'success': response.success,
                'channel': 'whatsapp',
                'whatsapp_id': response.message_id,
                'error': response.error_message
            }
        except Exception as e:
            logger.error(f'Erro ao enviar menu: {e}')
            return {'success': False, 'error': str(e)}

    def process_inbound_response(self, message: WhatsAppMessage) -> dict:
        """
        Processar resposta inbound do utilizador.
        
        Args:
            message: WhatsAppMessage instance (inbound)
        
        Returns:
            Dict com ação tomada
        """
        response = message.inbound_response.upper().strip()
        
        # ✅ Marcar task como concluída
        if response in ['✅', 'OK', 'CONCLUIDO', 'CONCLUÍDO', 'FEITO', 'DONE']:
            return self._handle_task_completion(message)
        
        # 📸 Solicitar foto
        elif response in ['📸', 'FOTO', 'FOTOS', 'PHOTO']:
            return self._handle_photo_request(message)
        
        # 1 - Ver tarefas
        elif response in ['1', 'TAREFAS', 'TASKS']:
            return self._handle_list_tasks(message)
        
        # 2 - Atualizar progresso
        elif response in ['2', 'PROGRESSO', 'PROGRESS']:
            return self._handle_update_progress(message)
        
        # 3 - Falar com gestor
        elif response in ['3', 'GESTOR', 'MANAGER']:
            return self._handle_contact_manager(message)
        
        else:
            return {'success': False, 'action': 'unknown', 'message': 'Resposta não reconhecida'}

    def _handle_task_completion(self, message: WhatsAppMessage) -> dict:
        """Marcar tarefa como concluída."""
        # Buscar task mais recente do utilizador
        from apps.construction.models import ConstructionTask
        
        task = ConstructionTask.objects.filter(
            assigned_to=message.user,
            status__in=['PENDING', 'IN_PROGRESS']
        ).order_by('-due_date').first()
        
        if task:
            old_status = task.status
            task.status = 'COMPLETED'
            task.completed_at = timezone.now()
            task.save(update_fields=['status', 'completed_at'])
            
            # Enviar confirmação
            self.whatsapp_client.send_free_text(
                to_phone=message.phone_number,
                message=f'✅ Tarefa "{task.name}" marcada como concluída!'
            )
            
            message.mark_processed()
            return {
                'success': True,
                'action': 'task_completed',
                'task_id': str(task.id),
                'previous_status': old_status
            }
        else:
            self.whatsapp_client.send_free_text(
                to_phone=message.phone_number,
                message='Não encontrei tarefas pendentes para marcar como concluídas.'
            )
            return {'success': False, 'action': 'no_pending_tasks'}

    def _handle_photo_request(self, message: WhatsAppMessage) -> dict:
        """Solicitar envio de fotos."""
        self.whatsapp_client.send_free_text(
            to_phone=message.phone_number,
            message=(
                '📸 *Envio de Fotos*\n\n'
                'Por favor, envie as fotos diretamente por aqui. '
                'Elas serão associadas ao relatório de obra de hoje.'
            )
        )
        message.mark_processed()
        return {'success': True, 'action': 'photo_requested'}

    def _handle_list_tasks(self, message: WhatsAppMessage) -> dict:
        """Listar tarefas do utilizador."""
        from apps.construction.models import ConstructionTask
        
        tasks = ConstructionTask.objects.filter(
            assigned_to=message.user,
            status__in=['PENDING', 'IN_PROGRESS']
        ).order_by('due_date')[:5]
        
        if tasks:
            text = '📋 *Suas Tarefas*\n\n'
            for i, task in enumerate(tasks, 1):
                status_emoji = '⏳' if task.status == 'PENDING' else '🔄'
                text += f'{i}. {status_emoji} {task.name} (até {task.due_date})\n'
            text += '\n_Responda ✅ para marcar a mais recente como concluída_'
        else:
            text = '✨ Não tem tarefas pendentes!'
        
        self.whatsapp_client.send_free_text(
            to_phone=message.phone_number,
            message=text
        )
        message.mark_processed()
        return {'success': True, 'action': 'list_tasks', 'count': len(tasks)}

    def _handle_update_progress(self, message: WhatsAppMessage) -> dict:
        """Solicitar atualização de progresso."""
        self.whatsapp_client.send_free_text(
            to_phone=message.phone_number,
            message=(
                '📊 *Atualizar Progresso*\n\n'
                'Qual a percentagem de conclusão?\n'
                'Responda com um número (ex: 75 para 75%)'
            )
        )
        message.mark_processed()
        return {'success': True, 'action': 'progress_requested'}

    def _handle_contact_manager(self, message: WhatsAppMessage) -> dict:
        """Encaminhar para gestor."""
        # TODO: Implementar notificação ao gestor
        self.whatsapp_client.send_free_text(
            to_phone=message.phone_number,
            message=(
                '👔 *Falar com Gestor*\n\n'
                'O seu pedido foi encaminhado. '
                'O gestor entrará em contacto em breve.'
            )
        )
        message.mark_processed()
        return {'success': True, 'action': 'manager_contacted'}
