import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from simple_history.models import HistoricalRecords

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('O email é obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('gestor', 'Gestor de Projecto'),
        ('vendedor', 'Vendedor'),
        ('engenheiro', 'Engenheiro de Obra'),
        ('investidor', 'Investidor'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='gestor')
    
    # Audit
    # AbstractUser already has date_joined (created_at equivalent)
    updated_at = models.DateTimeField(auto_now=True)
    
    history = HistoricalRecords()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    class Meta:
        ordering = ['email']
        verbose_name = 'utilizador'
        verbose_name_plural = 'utilizadores'

    def __str__(self) -> str:
        return self.email
