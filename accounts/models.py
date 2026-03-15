from django.db import models
from django.contrib.auth.models import User
import uuid


class Empleado(models.Model):
    OPCIONES_ROL = (
        ("empleado", "Empleado"),
        ("administrador", "Administrador"),
        ("restaurante", "Restaurante"),
    )

    usuario = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="perfil_empleado"
    )
    numero_documento = models.CharField(max_length=50, unique=True)
    departamento = models.CharField(max_length=100, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    rol = models.CharField(max_length=20, choices=OPCIONES_ROL, default="empleado")
    esta_activo = models.BooleanField(default=True)
    codigo_qr = models.UUIDField(default=uuid.uuid4, editable=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.usuario.first_name} {self.usuario.last_name} - {self.numero_documento}"
