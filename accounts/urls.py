from django.urls import path
from .views import crear_empleado, asignar_rol

urlpatterns = [
    path("empleados/crear/", crear_empleado, name="crear_empleado"),
    path("empleados/<int:empleado_id>/asignar-rol/", asignar_rol, name="asignar_rol"),
]
