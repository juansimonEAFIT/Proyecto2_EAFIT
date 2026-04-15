from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.conf import settings
from users.models import Empleado


class Consumo(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_consumo = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.empleado.user.username} consumió un tiquete el {self.fecha_consumo}"


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
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Si es una solicitud nueva o sigue pendiente, intentamos actualizar el precio unitario
        # del inventario más reciente. Esto asegura que si el administrador cambia el precio
        # antes de que se apruebe, la solicitud tome el precio final vigente.
        if not self.pk or self.estado == 'pendiente':
            inventario = InventarioTiquetes.objects.order_by("-mes").first()
            if inventario:
                self.precio_unitario = inventario.precio_tiquete
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado.user.username} - {self.cantidad} a ${self.precio_unitario} - {self.estado}"


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
    confirmado_por_empleado = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago {self.empleado.user.username} - ${self.valor_pagado} - Val: {self.validado_por_gh} - Conf: {self.confirmado_por_empleado}"

    def save(self, *args, **kwargs):
        nuevo = self.pk is None
        super().save(*args, **kwargs)

        if nuevo and self.validado_por_gh:
            self.empleado.saldo += self.valor_pagado
            self.empleado.save()