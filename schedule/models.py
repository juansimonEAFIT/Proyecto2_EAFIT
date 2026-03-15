from django.db import models
from django.utils import timezone
from accounts.models import Empleado


class ConsumoAlmuerzo(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="consumos_almuerzo"
    )
    fecha = models.DateField(default=timezone.localdate)
    hora_registro = models.DateTimeField(auto_now_add=True)
    valor_almuerzo = models.DecimalField(max_digits=10, decimal_places=2, default=15000.00)
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ("empleado", "fecha")

    def __str__(self):
        return f"{self.empleado.usuario.username} - {self.fecha}"


class SolicitudTiquete(models.Model):
    OPCIONES_TIPO = (
        ("fisico", "Físico"),
        ("qr", "Código QR"),
    )

    OPCIONES_ESTADO = (
        ("pendiente", "Pendiente"),
        ("aprobado", "Aprobado"),
        ("rechazado", "Rechazado"),
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="solicitudes_tiquete"
    )
    tipo_tiquete = models.CharField(max_length=20, choices=OPCIONES_TIPO)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default="pendiente")

    def __str__(self):
        return f"{self.empleado.usuario.username} - {self.tipo_tiquete} - {self.estado}"
