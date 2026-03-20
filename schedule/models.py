from django.db import models
from django.utils import timezone
from django.conf import settings
from accounts.models import Empleado


class InventarioTiquetes(models.Model):
    mes = models.DateField(default=timezone.now)
    cantidad_inicial = models.PositiveIntegerField()
    cantidad_disponible = models.PositiveIntegerField()
    max_tiquetes_por_empleado = models.PositiveIntegerField(default=20)
    precio_tiquete = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

    class Meta:
        verbose_name_plural = "Inventarios de Tiquetes"

    def __str__(self):
        return f"Inventario {self.mes.strftime('%B %Y')} - Disp: {self.cantidad_disponible}"


class ConsumoAlmuerzo(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="consumos_almuerzo"
    )
    fecha = models.DateField(default=timezone.localdate)
    hora_registro = models.DateTimeField(auto_now_add=True)
    valor_almuerzo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pagado = models.BooleanField(default=False)

    class Meta:
        unique_together = ("empleado", "fecha")

    def __str__(self):
        return f"{self.empleado.usuario.username} - {self.fecha}"


class SolicitudTiquete(models.Model):
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
    cantidad = models.PositiveIntegerField(default=1)
    fecha_reclamo = models.DateField(null=True, blank=True)
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=OPCIONES_ESTADO, default="pendiente")

    def __str__(self):
        return f"{self.empleado.usuario.username} - {self.cantidad} {self.tipo_tiquete} - {self.estado}"


class RegistroPago(models.Model):
    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.CASCADE,
        related_name="pagos_registrados"
    )
    valor_pagado = models.DecimalField(max_digits=12, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    comprobante = models.CharField(max_length=255, help_text="Referencia o link al comprobante", blank=True)
    validado_por_gh = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago {self.empleado.usuario.username} - ${self.valor_pagado} - Val: {self.validado_por_gh}"
