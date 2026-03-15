from django.contrib import admin
from .models import ConsumoAlmuerzo, SolicitudTiquete


@admin.register(ConsumoAlmuerzo)
class ConsumoAlmuerzoAdmin(admin.ModelAdmin):
    list_display = ("empleado", "fecha", "hora_registro")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("fecha",)


@admin.register(SolicitudTiquete)
class SolicitudTiqueteAdmin(admin.ModelAdmin):
    list_display = ("empleado", "tipo_tiquete", "estado", "fecha_solicitud")
    search_fields = ("empleado__usuario__username",)
    list_filter = ("tipo_tiquete", "estado", "fecha_solicitud")
