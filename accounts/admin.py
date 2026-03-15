from django.contrib import admin
from .models import Empleado


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "numero_documento",
        "departamento",
        "rol",
        "esta_activo",
        "fecha_creacion",
    )
    search_fields = (
        "usuario__first_name",
        "usuario__last_name",
        "usuario__username",
        "numero_documento",
    )
    list_filter = ("rol", "esta_activo", "departamento")
