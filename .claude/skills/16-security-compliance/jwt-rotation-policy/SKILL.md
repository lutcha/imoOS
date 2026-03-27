---
name: jwt-rotation-policy
description: Access token de 15 minutos, refresh token de 7 dias com ROTATE_REFRESH_TOKENS=True, blacklist via django-rest-framework-simplejwt TokenBlacklist e Redis para lookups rápidos.
argument-hint: ""
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Implementar uma política de rotação de tokens JWT segura que minimiza o impacto de tokens roubados. A combinação de tokens de curta duração com blacklist no Redis garante revogação imediata quando necessário.

## Code Pattern

```python
# settings/base.py
from datetime import timedelta

INSTALLED_APPS += ["rest_framework_simplejwt.token_blacklist"]

SIMPLE_JWT = {
    # Tokens de curta duração — minimiza impacto de roubo
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),

    # Rotação automática — novo refresh token a cada uso
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,  # invalidar o refresh anterior após rotação

    # Segurança
    "ALGORITHM": "HS256",
    "SIGNING_KEY": config("DJANGO_SECRET_KEY"),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),

    # Adicionar claims personalizados
    "TOKEN_OBTAIN_SERIALIZER": "auth.serializers.CustomTokenObtainPairSerializer",
}
```

```python
# auth/serializers.py — claims personalizados no JWT
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.db import connection

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Adicionar claims personalizados
        token["tenant_schema"] = connection.schema_name
        token["role"] = getattr(user, "profile", None) and user.profile.role or "user"
        token["email"] = user.email
        return token
```

```python
# auth/views.py — logout com blacklist
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.cache import cache

class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"error": "refresh token obrigatório."}, status=400)

        try:
            token = RefreshToken(refresh_token)

            # 1. Blacklist na base de dados (django-simplejwt)
            token.blacklist()

            # 2. Cache Redis para lookup ultra-rápido (antes da DB)
            jti = token["jti"]
            exp = token["exp"]
            ttl = exp - int(__import__("time").time())
            if ttl > 0:
                cache.set(f"blacklisted_jti:{jti}", True, timeout=ttl)

        except Exception:
            pass  # Token inválido ou expirado — logout bem-sucedido na mesma

        return Response({"message": "Sessão terminada com sucesso."})
```

```python
# auth/authentication.py — verificação rápida via Redis
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.cache import cache

class CachedJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get("jti")
        if cache.get(f"blacklisted_jti:{jti}"):
            from rest_framework_simplejwt.exceptions import TokenError
            raise TokenError("Token está na blacklist.")
        return token
```

## Key Rules

- `ACCESS_TOKEN_LIFETIME = 15 minutos` — o cliente deve renovar o token silenciosamente antes da expiração.
- `ROTATE_REFRESH_TOKENS = True` invalida o refresh anterior após cada uso — previne reuso de tokens roubados.
- Verificar a blacklist Redis antes da base de dados — reduz latência de autenticação em ~90%.
- Nunca armazenar tokens de acesso em `localStorage` — usar `httpOnly cookie` ou memória.

## Anti-Pattern

```python
# ERRADO: tokens de longa duração sem rotação
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),  # token roubado válido por 30 dias
    "ROTATE_REFRESH_TOKENS": False,                # refresh reutilizável indefinidamente
}
```
