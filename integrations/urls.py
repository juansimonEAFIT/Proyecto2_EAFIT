from django.urls import path
from .views import ver_qr_empleado, consumir_almuerzo_qr

urlpatterns = [
    path("mi-qr/", ver_qr_empleado, name="ver_qr_empleado"),
    path("almuerzo/consumir/<uuid:codigo_qr>/<str:token>/", consumir_almuerzo_qr, name="consumir_almuerzo_qr"),
]
