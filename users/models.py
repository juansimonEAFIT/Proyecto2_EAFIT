from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
import uuid


# ========== USER BASE ==========

class User(AbstractUser):
    """
    Usuario base del sistema.
    Representa identidad, autenticación y rol principal.
    """

    ROLES = (
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador'),
        ('restaurante', 'Restaurante'),
    )

    role = models.CharField(max_length=20, choices=ROLES, default='empleado')
    qr_token = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


# ========== PERFILES POR ROL ==========

class Empleado(models.Model):
    """
    Perfil exclusivo de usuarios con rol EMPLEADO.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="empleado_perfil"
    )

    numero_documento = models.CharField(max_length=50, unique=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)

    codigo_qr = models.UUIDField(default=uuid.uuid4, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    saldo = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Empleado: {self.user.get_full_name() or self.user.username}"


class Restaurante(models.Model):
    """
    Perfil exclusivo de usuarios con rol RESTAURANTE.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="restaurante_perfil"
    )

    nombre_sede = models.CharField(max_length=100, default="Sede Principal")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Restaurante: {self.nombre_sede} ({self.user.username})"


class Administrador(models.Model):
    """
    Perfil exclusivo de usuarios con rol ADMINISTRADOR.
    """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="administrador_perfil"
    )

    cargo = models.CharField(max_length=100, default="Gestión Humana")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Administrador: {self.user.get_full_name() or self.user.username}"