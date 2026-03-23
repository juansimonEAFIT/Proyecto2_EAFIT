from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.conf import settings
from users.models import Empleado
from datetime import time
from django.db.models import Sum

# Una funcion util para obtener la hora
def hora_actual():
    return timezone.now().time()

# Mixin para guardar Intervalos de tiempo
class IntervaloTiempoMixin(models.Model):
    desde = models.TimeField(blank=True, null=True)
    hasta = models.TimeField(blank=True, null=True)

    class Meta:
        abstract = True

    def clean(self):
        if self.desde and self.hasta:
            if self.hasta <= self.desde:
                raise ValidationError("La hora final debe ser mayor a la inicial.")

# Tabla donde se almacena toda la información relacionada a las comidas
class Comida(models.Model):
    fecha_de_creacion = models.DateField(default=timezone.localdate)
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField(max_length=255)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

    def __str__(self):
        return f"{self.nombre} ({self.fecha_de_creacion})"

# Esto es para las comidas que se van a reservar ya empleado por empleado
class ComidaReservada(IntervaloTiempoMixin, models.Model):
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE)
    fecha_de_consumo = models.DateField(default=timezone.localdate)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.comida} ({self.fecha_de_consumo})"

# Tabla que guardara todos los almuerzos al igual que establece intervalos por default para esos valores(esto es mas que todo si se llega crear otras cosas como desayunos o cena)
class Almuerzo(ComidaReservada):
    #Si es necesario colocar algo que solo se llegara a ser necesario para los almuerzos colocar aqui
    def save(self, *args, **kwargs):
        # Defaults SOLO si no están definidos
        self.tipo = "almuerzo"
        if self.desde is None:
            self.desde = time(11, 0)
        if self.hasta is None:
            self.hasta = time(14, 0)

        super().save(*args, **kwargs)

# Lleva todas las comidas consumidas y ya distribuidas con la fecha en la que se consumieron el usuario y que comida se consumio
class Consumo(models.Model):
    comida = models.ForeignKey(ComidaReservada, on_delete=models.CASCADE)   # ← CAMBIO IMPORTANTE
    fecha_consumo = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("comida",)

    def __str__(self):
        return f"{self.comida.empleado} consumió {self.comida.comida.nombre} el {self.fecha_consumo}"

# Lleva que comidas tiene programadas un usuario para que dia y fecha, todo esto sera configurado claramente por un empleado de la empresa distribuidora
class Schedule(models.Model):
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    comida = models.ManyToManyField(ComidaReservada, blank=True)

    def __str__(self):
        return f"Schedule de {self.empleado}"

    def add_comida(self, comida):
        if comida.empleado != self.empleado:
            raise ValidationError("No puedes asignar una comida de otro empleado.")
        self.comida.add(comida)

    def consumir(self, comida: ComidaReservada):
        ahora = hora_actual()
        if comida.desde and ahora < comida.desde:
            raise ValidationError(
                "No se puede reclamar en este momento; verifique el horario permitido."
            )

        if comida.hasta and ahora > comida.hasta:
            raise ValidationError(
                "No se puede reclamar en este momento; verifique el horario permitido."
            )

        if comida.empleado != self.empleado:
            raise ValidationError("Esta comida no pertenece a este empleado.")

        consumo = Consumo.objects.create(
            empleado=self.empleado,
            comida=comida
        )

        # Descontar saldo
        empleado_perfil = self.empleado
        empleado_perfil.saldo -= comida.comida.precio
        empleado_perfil.save()

        self.comida.remove(comida)

        return consumo

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
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=10000.00)

    def save(self, *args, **kwargs):
        if not self.pk:
            inventario = InventarioTiquetes.objects.order_by("-mes").first()
            if inventario:
                self.precio_unitario = inventario.precio_tiquete
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.empleado.usuario.username} - {self.cantidad} a ${self.precio_unitario} - {self.estado}"


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

    def save(self, *args, **kwargs):
        nuevo = self.pk is None
        super().save(*args, **kwargs)

        if nuevo and self.validado_por_gh:
            self.empleado.saldo += self.valor_pagado
            self.empleado.save()

    from django.db.models import Sum

    def recalcular_saldo(empleado):
        total_pagos = RegistroPago.objects.filter(
            empleado=empleado, validado_por_gh=True
        ).aggregate(Sum("valor_pagado"))["valor_pagado__sum"] or 0

        total_consumos = Consumo.objects.filter(
            comida__empleado=empleado
        ).aggregate(
            Sum("comida__comida__precio")
        )["comida__comida__precio__sum"] or 0

        return total_pagos - total_consumos