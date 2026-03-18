from django.contrib import admin
from .models import (
    ConsumoAlmuerzo, SolicitudTiquete, InventarioTiquetes, 
    MenuItem, FoodCalendar, RegistroPago
)


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio", "stock")


@admin.register(FoodCalendar)
class FoodCalendarAdmin(admin.ModelAdmin):
    list_display = ("nombre", "fecha_inicio", "fecha_fin")
    filter_horizontal = ("items", "empleados")


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
    list_display = ("empleado", "tipo_tiquete", "cantidad", "estado", "fecha_solicitud")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("tipo_tiquete", "estado", "fecha_solicitud")


@admin.register(RegistroPago)
class RegistroPagoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "valor_pagado", "fecha_pago", "validado_por_gh")
    list_filter = ("validado_por_gh", "fecha_pago")
