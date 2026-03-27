---
name: project-team-assignment
description: Modelo ProjectMember com user/project/role, herança de permissões por projeto e registo de atividade.
argument-hint: "[project_id] [user_id] [role]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir a equipa de um projeto com papéis específicos (gestor, engenheiro, comercial, etc.). As permissões são herdadas do papel no projeto e o log de atividade regista todas as ações relevantes.

## Code Pattern

```python
# projects/models.py
from django.db import models
from django.conf import settings

class ProjectRole(models.TextChoices):
    MANAGER = "MANAGER", "Gestor de Projeto"
    ENGINEER = "ENGINEER", "Engenheiro"
    SALES = "SALES", "Comercial"
    INVESTOR = "INVESTOR", "Investidor"
    VIEWER = "VIEWER", "Visualizador"

class ProjectMember(models.Model):
    project = models.ForeignKey("Project", on_delete=models.CASCADE, related_name="members")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ProjectRole.choices)
    added_at = models.DateTimeField(auto_now_add=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, related_name="added_members"
    )

    class Meta:
        unique_together = ("project", "user")

    def can_edit(self) -> bool:
        return self.role in [ProjectRole.MANAGER, ProjectRole.ENGINEER]

    def can_approve(self) -> bool:
        return self.role == ProjectRole.MANAGER
```

```python
# projects/permissions.py
from rest_framework.permissions import BasePermission
from .models import ProjectMember

class IsProjectMember(BasePermission):
    def has_object_permission(self, request, view, obj):
        return ProjectMember.objects.filter(
            project=obj, user=request.user
        ).exists()

class CanEditProject(BasePermission):
    def has_object_permission(self, request, view, obj):
        try:
            member = ProjectMember.objects.get(project=obj, user=request.user)
            return member.can_edit()
        except ProjectMember.DoesNotExist:
            return False
```

```python
# projects/activity_log.py
from django.utils import timezone

def log_activity(project, user, action: str, details: dict = None):
    from .models import ProjectActivityLog
    ProjectActivityLog.objects.create(
        project=project,
        user=user,
        action=action,
        details=details or {},
        timestamp=timezone.now(),
    )
```

## Key Rules

- Um utilizador só pode ter um papel por projeto (`unique_together = ("project", "user")`).
- Apenas `MANAGER` pode adicionar ou remover membros da equipa.
- Registar no `ProjectActivityLog` todas as alterações de membros, progresso e estado.
- O papel `INVESTOR` só tem permissão de leitura — nunca escrita.

## Anti-Pattern

```python
# ERRADO: verificar permissões com base no papel global do utilizador
if request.user.is_staff:  # ignora o papel específico no projeto
    allow_edit()
```
