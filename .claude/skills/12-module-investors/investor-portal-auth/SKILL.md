---
name: investor-portal-auth
description: Papel Investidor com permissões só de leitura, fluxo de login separado em /investor/login, 2FA via TOTP (pyotp) e log de auditoria de sessão.
argument-hint: "[investor_user_id]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Fornecer acesso seguro ao portal de investidores com autenticação de dois fatores obrigatória. O papel `INVESTOR` tem acesso apenas de leitura a relatórios e KPIs do seu projeto, sem acesso a dados operacionais.

## Code Pattern

```python
# investors/models.py
import pyotp
from django.db import models
from django.conf import settings

class InvestorProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="investor_profile")
    totp_secret = models.CharField(max_length=32, blank=True)
    totp_enabled = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    def get_totp(self) -> pyotp.TOTP:
        if not self.totp_secret:
            self.totp_secret = pyotp.random_base32()
            self.save(update_fields=["totp_secret"])
        return pyotp.TOTP(self.totp_secret)

    def verify_totp(self, code: str) -> bool:
        return self.get_totp().verify(code, valid_window=1)

    def get_totp_provisioning_uri(self) -> str:
        return self.get_totp().provisioning_uri(
            name=self.user.email, issuer_name="ImoOS"
        )
```

```python
# investors/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

class InvestorLoginView(APIView):
    """POST /investor/login/ — passo 1: credenciais"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        from django.contrib.auth import authenticate
        user = authenticate(
            username=request.data.get("email"),
            password=request.data.get("password"),
        )
        if not user or not hasattr(user, "investor_profile"):
            return Response({"error": "Credenciais inválidas."}, status=401)

        if user.investor_profile.totp_enabled:
            # Retornar token temporário para passo 2 (TOTP)
            import jwt
            temp_token = jwt.encode(
                {"user_id": user.id, "step": "totp"},
                settings.SECRET_KEY, algorithm="HS256"
            )
            return Response({"requires_2fa": True, "temp_token": temp_token})

        return self._issue_tokens(user, request)


class InvestorTOTPVerifyView(APIView):
    """POST /investor/login/totp/ — passo 2: código TOTP"""
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        import jwt
        try:
            payload = jwt.decode(request.data["temp_token"], settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.InvalidTokenError:
            return Response({"error": "Token inválido."}, status=401)

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(id=payload["user_id"])

        if not user.investor_profile.verify_totp(request.data.get("code", "")):
            InvestorSessionAuditLog.objects.create(user=user, event="2FA_FAILED", ip=get_client_ip(request))
            return Response({"error": "Código TOTP inválido."}, status=401)

        InvestorSessionAuditLog.objects.create(user=user, event="LOGIN_SUCCESS", ip=get_client_ip(request))
        return self._issue_tokens(user, request)
```

## Key Rules

- O 2FA via TOTP é obrigatório para todos os utilizadores com papel `INVESTOR` — não é opcional.
- O portal de investidores (`/investor/`) deve usar um subdomínio separado ou prefixo distinto do painel operacional.
- Registar cada login, tentativa falhada e logout em `InvestorSessionAuditLog` com IP e timestamp.
- O papel `INVESTOR` nunca deve ter permissão de escrita — usar `IsAuthenticatedInvestorReadOnly` permission class.

## Anti-Pattern

```python
# ERRADO: usar o mesmo endpoint de login para investidores e staff operacional
# Misturar fluxos dificulta o enforcement de 2FA obrigatório para investidores
```
