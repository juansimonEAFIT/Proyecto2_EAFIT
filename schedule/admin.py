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
        "empleado_responsable",
        "nombre_comida",
        "fecha_consumo",
    )

    list_filter = (
        "comida__empleado",
        "comida__comida__nombre",
        "fecha_consumo",
    )

    search_fields = (
        "comida__empleado__usuario__username",
        "comida__comida__nombre",
        "fecha_consumo",
    )

    # === Métodos auxiliares para mostrar datos relacionados ===

    def empleado_responsable(self, obj):
        return obj.comida.empleado
    empleado_responsable.short_description = "Empleado"

    def nombre_comida(self, obj):
        return obj.comida.comida.nombre
    nombre_comida.short_description = "Comida"

@admin.register(SolicitudTiquete)
class SolicitudTiqueteAdmin(admin.ModelAdmin):
    list_display = ("empleado", "cantidad", "estado", "fecha_solicitud")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("estado", "fecha_solicitud")


@admin.register(RegistroPago)
class RegistroPagoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "valor_pagado", "fecha_pago", "validado_por_gh")
    list_filter = ("validado_por_gh", "fecha_pago")
