from django.db import models
from django.conf import settings
import uuid


class Empleado(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_empleado"
    )
    numero_documento = models.CharField(max_length=50, unique=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    esta_activo = models.BooleanField(default=True)
    codigo_qr = models.UUIDField(default=uuid.uuid4, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Empleado: {self.usuario.get_full_name() or self.usuario.username}"


class Restaurante(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_restaurante"
    )
    nombre_sede = models.CharField(max_length=100, default="Sede Principal")
    telefono = models.CharField(max_length=20, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Restaurante: {self.nombre_sede} ({self.usuario.username})"


class Administrador(models.Model):
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="perfil_administrador"
    )
    cargo = models.CharField(max_length=100, default="Gestión Humana")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Admin: {self.usuario.get_full_name() or self.usuario.username}"
