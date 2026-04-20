from django.urls import path
from .views import inicio, dashboard_empleado, dashboard_admin, dashboard_restaurante, dashboard_reportes

urlpatterns = [
    path("", inicio, name="inicio"),
    path("dashboard/", dashboard_empleado, name="dashboard_empleado"),
    path("gestion-humana/", dashboard_admin, name="dashboard_admin"),
    path("gestion-humana/reportes/", dashboard_reportes, name="dashboard_reportes"),
    path("restaurante/", dashboard_restaurante, name="dashboard_restaurante"),
]
