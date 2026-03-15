from django.urls import path
from .views import (
    consumir_almuerzo_qr,
    solicitar_tiquete,
    lista_solicitudes_admin,
    consultar_estado_cuenta,
)

urlpatterns = [
    path("almuerzo/consumir/<uuid:codigo_qr>/", consumir_almuerzo_qr, name="consumir_almuerzo_qr"),
    path("tiquetes/solicitar/", solicitar_tiquete, name="solicitar_tiquete"),
    path("admin/solicitudes/", lista_solicitudes_admin, name="lista_solicitudes_admin"),
    path("empleados/<int:empleado_id>/estado-cuenta/", consultar_estado_cuenta, name="consultar_estado_cuenta"),
]
