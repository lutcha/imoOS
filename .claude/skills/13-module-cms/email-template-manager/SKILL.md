---
name: email-template-manager
description: Modelo EmailTemplate com subject/html_body/text_body/variables JSON, função render_template(name, context) e UI de admin para edição e envio de teste.
argument-hint: "[template_name] [context_json]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Centralizar a gestão de templates de email por inquilino. Os templates são editáveis pelo admin sem necessidade de deploy, e a função `render_template` abstrai a renderização para uso em qualquer parte do sistema.

## Code Pattern

```python
# cms/models.py
from django.db import models

class EmailTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True, help_text="ex: welcome_email, payment_reminder")
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=255, help_text="Suporta variáveis: {{ buyer_name }}")
    html_body = models.TextField(help_text="HTML completo com variáveis Django template")
    text_body = models.TextField(help_text="Versão texto simples para clientes sem suporte HTML")
    variables = models.JSONField(
        default=list,
        help_text='Lista de variáveis disponíveis: ["buyer_name", "amount_cve", "due_date"]'
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)
    updated_by = models.ForeignKey("auth.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["name"]
```

```python
# cms/services.py
from django.template import Context, Template
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def render_template(name: str, context: dict) -> dict:
    """
    Renderiza um EmailTemplate com o contexto fornecido.
    Retorna {"subject": ..., "html_body": ..., "text_body": ...}
    """
    try:
        template = EmailTemplate.objects.get(name=name, is_active=True)
    except EmailTemplate.DoesNotExist:
        raise ValueError(f"Template de email '{name}' não encontrado ou inativo.")

    ctx = Context(context)
    return {
        "subject": Template(template.subject).render(ctx),
        "html_body": Template(template.html_body).render(ctx),
        "text_body": Template(template.text_body).render(ctx),
    }


def send_templated_email(template_name: str, context: dict, recipient_email: str):
    """Envia email usando um template pelo nome."""
    rendered = render_template(template_name, context)
    msg = EmailMultiAlternatives(
        subject=rendered["subject"],
        body=rendered["text_body"],
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient_email],
    )
    msg.attach_alternative(rendered["html_body"], "text/html")
    msg.send()
```

```python
# cms/admin.py — UI para envio de teste
from django.contrib import admin
from django.http import HttpResponseRedirect

@admin.register(EmailTemplate)
class EmailTemplateAdmin(admin.ModelAdmin):
    list_display = ["name", "subject", "is_active", "updated_at"]
    actions = ["send_test_email"]

    def send_test_email(self, request, queryset):
        for template in queryset[:1]:
            test_context = {var: f"[{var.upper()}]" for var in template.variables}
            send_templated_email(template.name, test_context, request.user.email)
        self.message_user(request, "Email de teste enviado.")
    send_test_email.short_description = "Enviar email de teste"
```

## Key Rules

- Usar `django.template.Template` para renderizar — suporta filtros e tags como `{{ amount|floatformat:0 }}`.
- O campo `variables` documenta as variáveis disponíveis — validar que o contexto as contém antes de renderizar.
- Templates devem sempre ter versão `text_body` para clientes de email que não suportam HTML.
- Registar no log de auditoria quando um template é modificado — campo `updated_by`.

## Anti-Pattern

```python
# ERRADO: usar str.replace() para substituição de variáveis
html = template.html_body.replace("{{buyer_name}}", context["buyer_name"])  # sem filtros, sem escape HTML
```
