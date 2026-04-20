from django.urls import path
from .views import (
    solicitar_tiquete,
    registrar_pago,
    gestionar_solicitud,
    consultar_estado_cuenta,
    gestionar_inventario,
    aumentar_inventario,
    historial_consumos_restaurante,
    historial_consumos,
    confirmar_pago_empleado,
    registrar_pago_efectivo,
    editar_consumo,
    exportar_reporte_consumos,
    exportar_reporte_pagos,
)

urlpatterns = [
    path("estado-cuenta/", consultar_estado_cuenta, name="consultar_estado_cuenta"),
    path("tiquetes/solicitar/", solicitar_tiquete, name="solicitar_tiquete"),
    path("pagos/registrar/", registrar_pago, name="registrar_pago"),
    path("gestion-humana/inventario/", gestionar_inventario, name="gestionar_inventario"),
    path("gestion-humana/inventario/aumentar/", aumentar_inventario, name="aumentar_inventario"),
    path("gestion-humana/solicitud/<int:solicitud_id>/<str:accion>/", gestionar_solicitud, name="gestionar_solicitud"),
    path("gestion-humana/pago/registrar/", registrar_pago_efectivo, name="registrar_pago_efectivo"),
    path("gestion-humana/reportes/consumos/", exportar_reporte_consumos, name="exportar_reporte_consumos"),
    path("gestion-humana/reportes/pagos/", exportar_reporte_pagos, name="exportar_reporte_pagos"),
    path("empleado/pago/<int:pago_id>/confirmar/", confirmar_pago_empleado, name="confirmar_pago_empleado"),
    path("restaurante/consumos/", historial_consumos_restaurante, name="historial_consumos_restaurante"),
    path("gestion-humana/empleado/<int:empleado_id>/consumos/", historial_consumos, name="historial_consumos"),
    path("gestion-humana/consumo/<int:consumo_id>/editar/", editar_consumo, name="editar_consumo"),
]
