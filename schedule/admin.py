from django.contrib import admin
from .models import (
    Consumo, SolicitudTiquete, InventarioTiquetes,
    RegistroPago
)

@admin.register(InventarioTiquetes)
class InventarioTiquetesAdmin(admin.ModelAdmin):
    list_display = ("mes", "cantidad_inicial", "cantidad_disponible")

@admin.register(Consumo)
class ConsumoAdmin(admin.ModelAdmin):
    list_display = (
        "empleado",
        "fecha_consumo",
    )

    list_filter = (
        "empleado",
        "fecha_consumo",
    )

    search_fields = (
        "empleado__user__username",
        "fecha_consumo",
    )

@admin.register(SolicitudTiquete)
class SolicitudTiqueteAdmin(admin.ModelAdmin):
    list_display = ("empleado", "cantidad", "estado", "fecha_solicitud")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("estado", "fecha_solicitud")


@admin.register(RegistroPago)
class RegistroPagoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "valor_pagado", "fecha_pago", "validado_por_gh")
    list_filter = ("validado_por_gh", "fecha_pago")
