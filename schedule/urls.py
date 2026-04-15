from django.urls import path
from .views import (
    solicitar_tiquete,
    registrar_pago,
    gestionar_solicitud,
    consultar_estado_cuenta,
    gestionar_inventario,
    aumentar_inventario,
    historial_consumos_restaurante,
    confirmar_pago_empleado,
    registrar_pago_efectivo
)

urlpatterns = [
    path("estado-cuenta/", consultar_estado_cuenta, name="consultar_estado_cuenta"),
    path("tiquetes/solicitar/", solicitar_tiquete, name="solicitar_tiquete"),
    path("pagos/registrar/", registrar_pago, name="registrar_pago"),
    path("gestion-humana/inventario/", gestionar_inventario, name="gestionar_inventario"),
    path("gestion-humana/inventario/aumentar/", aumentar_inventario, name="aumentar_inventario"),
    path("gestion-humana/solicitud/<int:solicitud_id>/<str:accion>/", gestionar_solicitud, name="gestionar_solicitud"),
    path("gestion-humana/pago/registrar/", registrar_pago_efectivo, name="registrar_pago_efectivo"),
    path("empleado/pago/<int:pago_id>/confirmar/", confirmar_pago_empleado, name="confirmar_pago_empleado"),
    path("restaurante/consumos/", historial_consumos_restaurante, name="historial_consumos_restaurante"),
]