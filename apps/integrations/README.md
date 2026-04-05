# WhatsApp Business API Integration

Módulo de integração com WhatsApp Business API para o ImoOS.
Permite comunicação automatizada com equipas de obra via WhatsApp.

## Funcionalidades

- **Envio de Mensagens Templates**: Templates aprovados pela Meta
- **Texto Livre**: Dentro da janela de 24h da conversa
- **Menus Interativos**: Botões de ação rápida
- **Recebimento de Respostas**: Webhooks para processar respostas
- **Notificações Automáticas**: Tarefas atribuídas, atrasos, lembretes
- **Fallback Multi-canal**: WhatsApp → Email → SMS

## Arquitetura

```
apps/integrations/
├── models.py              # WhatsAppMessage, WhatsAppTemplate, NotificationPreference
├── services/
│   ├── whatsapp_client.py    # Cliente Twilio/Meta API
│   └── notification_router.py # Roteador de notificações
├── views.py               # Webhooks e API endpoints
├── urls.py                # Rotas da API
├── tasks.py               # Celery tasks async
├── signals.py             # Signals Django
├── admin.py               # Configuração do Admin
└── tests/                 # Testes unitários
```

## Configuração

### 1. Variáveis de Ambiente (.env)

```bash
# Provider: 'twilio' ou 'meta'
WHATSAPP_PROVIDER=meta

# Meta/WhatsApp Business API
WHATSAPP_PHONE_NUMBER_ID=123456789012345
WHATSAPP_ACCESS_TOKEN=EAAxxxxxxxxxxxxxxxx
WHATSAPP_API_VERSION=v18.0
WHATSAPP_BUSINESS_ID=123456789
WHATSAPP_VERIFY_TOKEN=imoos-webhook-token  # Para verificação do webhook

# Twilio (alternativa)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# Celery Beat - Scheduled Tasks
CELERY_BEAT_SCHEDULE='{"send-scheduled-reminders": {"task": "apps.integrations.tasks.send_scheduled_reminders", "schedule": 28800.0}, "check-overdue-tasks": {"task": "apps.integrations.tasks.check_overdue_tasks", "schedule": 86400.0}}'
```

### 2. Configurar Webhook na Meta

1. Acesse [Meta Developers](https://developers.facebook.com/)
2. Seu App → WhatsApp → Configuration
3. Webhook URL: `https://{tenant}.imos.cv/api/v1/integrations/webhook/`
4. Verify Token: Mesmo valor de `WHATSAPP_VERIFY_TOKEN`
5. Subscribe to: `messages`, `message_status`

### 3. Configurar Templates

Templates devem ser aprovados pela Meta antes do uso:

```python
from apps.integrations.models import WhatsAppTemplate

# Criar template
template = WhatsAppTemplate.objects.create(
    name='task_reminder',
    template_type='TASK_REMINDER',
    content_pt='Olá {{nome}}, a tarefa "{{tarefa}}" vence em {{data}}.',
    variables=['{{nome}}', '{{tarefa}}', '{{data}}'],
    meta_template_id='template_id_da_meta'
)
```

## Uso

### Enviar Mensagem de Teste

```bash
curl -X POST https://api.imos.cv/api/v1/integrations/send-test/ \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{
    "phone": "+2389991234",
    "message": "Teste de integração ✅"
  }'
```

### Notificar Atribuição de Tarefa

```python
from apps.integrations.services import NotificationRouter

router = NotificationRouter()
router.notify_task_assignment(task)
```

### Menu Interativo

```python
router.send_interactive_task_menu(user, phone='+2389991234')
```

Respostas suportadas:
- `1` ou "TAREFAS" - Ver tarefas pendentes
- `2` ou "PROGRESSO" - Atualizar progresso
- `3` ou "GESTOR" - Falar com gestor
- `✅` - Marcar tarefa como concluída
- `📸` - Solicitar envio de foto

## Celery Tasks

### Lembretes Diários (8h)
```python
# Enviado automaticamente via Celery Beat
send_scheduled_reminders.delay()
```

### Verificação de Atrasos
```python
check_overdue_tasks.delay()
```

### Processar Resposta
```python
process_inbound_message.delay(message_id)
```

## Webhook - Respostas

Quando um utilizador responde:

1. Meta envia POST para `/api/v1/integrations/webhook/`
2. Sistema cria `WhatsAppMessage` (inbound)
3. Task Celery `process_inbound_message` é disparada
4. Sistema processa ação baseada na resposta

Exemplo de resposta processada:

```json
{
  "success": true,
  "action": "task_completed",
  "task_id": "uuid-da-tarefa"
}
```

## Preferências do Utilizador

```bash
# Obter preferências
GET /api/v1/integrations/preferences/

# Atualizar
PUT /api/v1/integrations/preferences/ \
  -d '{
    "whatsapp_enabled": true,
    "email_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "08:00"
  }'
```

## Testes

```bash
# Rodar testes do app
python manage.py test apps.integrations.tests

# Com coverage
pytest apps/integrations/tests/ -v --cov=apps.integrations
```

## LGPD / Privacidade

- Mensagens são armazenadas por 90 dias (anonimizadas após)
- Logs não contêm conteúdo de mensagens em produção
- Opt-out respeitado para leads (`whatsapp_opt_out`)
- Dados de webhook brutos são limpos periodicamente

## Troubleshooting

### Mensagens não são entregues

1. Verificar se template está aprovado na Meta
2. Verificar se número está no formato internacional (+238...)
3. Verificar logs: `docker logs imos_celery_worker`
4. Verificar status na Meta: `https://business.facebook.com/wa/manage/`

### Webhook não recebe mensagens

1. Verificar URL do webhook está acessível externamente
2. Verificar `WHATSAPP_VERIFY_TOKEN` coincide
3. Verificar subscrição aos eventos corretos
4. Testar com `curl` simulando payload

### Erro "Não foi possível encontrar o template"

1. Verificar `meta_template_id` está correto
2. Verificar idioma do template (pt_PT vs pt_BR)
3. Verificar se variáveis correspondem exatamente

## Roadmap

- [ ] Suporte a mensagens de mídia (fotos, documentos)
- [ ] Listas interativas (mais de 3 opções)
- [ ] Templates dinâmicos com rich media
- [ ] Analytics de engajamento
- [ ] Fallback para SMS via Africa's Talking
