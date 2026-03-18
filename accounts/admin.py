from django.contrib import admin
from .models import Empleado, Administrador, Restaurante


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "numero_documento",
        "departamento",
        "esta_activo",
        "fecha_creacion",
    )
    search_fields = (
        "usuario__first_name",
        "usuario__last_name",
        "usuario__username",
        "numero_documento",
    )
    list_filter = ("esta_activo", "departamento")


@admin.register(Administrador)
class AdministradorAdmin(admin.ModelAdmin):
    list_display = ("usuario", "cargo", "fecha_creacion")
    search_fields = ("usuario__username", "cargo")


@admin.register(Restaurante)
class RestauranteAdmin(admin.ModelAdmin):
    list_display = ("usuario", "nombre_sede", "telefono", "fecha_creacion")
    search_fields = ("usuario__username", "nombre_sede")
