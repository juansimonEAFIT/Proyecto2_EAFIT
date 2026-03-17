from django.urls import path
from .views import (
    consumir_almuerzo_qr,
    solicitar_tiquete,
    registrar_pago,
    gestionar_solicitud,
    gestionar_pago,
    consultar_estado_cuenta,
    gestionar_inventario,
)

urlpatterns = [
    path("almuerzo/consumir/<uuid:codigo_qr>/", consumir_almuerzo_qr, name="consumir_almuerzo_qr"),
    path("estado-cuenta/", consultar_estado_cuenta, name="consultar_estado_cuenta"),
    path("tiquetes/solicitar/", solicitar_tiquete, name="solicitar_tiquete"),
    path("pagos/registrar/", registrar_pago, name="registrar_pago"),
    path("gestion-humana/inventario/", gestionar_inventario, name="gestionar_inventario"),
    path("gestion-humana/solicitud/<int:solicitud_id>/<str:accion>/", gestionar_solicitud, name="gestionar_solicitud"),
    path("gestion-humana/pago/<int:pago_id>/validar/", gestionar_pago, name="gestionar_pago"),
]