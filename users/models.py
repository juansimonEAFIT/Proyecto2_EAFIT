from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid

class User(AbstractUser):
    ROLES = (
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador'),
        ('restaurante', 'Restaurante'),
    )
    role = models.CharField(max_length=20, choices=ROLES, default='empleado')
    qr_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
