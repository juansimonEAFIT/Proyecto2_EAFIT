from django.contrib import admin
from .models import (
    ConsumoAlmuerzo, SolicitudTiquete, InventarioTiquetes, 
    RegistroPago
)

@admin.register(InventarioTiquetes)
class InventarioTiquetesAdmin(admin.ModelAdmin):
    list_display = ("mes", "cantidad_inicial", "cantidad_disponible")


@admin.register(ConsumoAlmuerzo)
class ConsumoAlmuerzoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha", "hora_registro", "pagado")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("fecha", "pagado")


@admin.register(SolicitudTiquete)
class SolicitudTiqueteAdmin(admin.ModelAdmin):
    list_display = ("empleado", "cantidad", "estado", "fecha_solicitud")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("estado", "fecha_solicitud")


@admin.register(RegistroPago)
class RegistroPagoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "valor_pagado", "fecha_pago", "validado_por_gh")
    list_filter = ("validado_por_gh", "fecha_pago")
