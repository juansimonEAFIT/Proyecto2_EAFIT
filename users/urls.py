from django.urls import path
from .views import gestionar_personal, perfil_usuario, editar_perfil, cambiar_estado_usuario, login_view, cambiar_contrasena

urlpatterns = [
    path("login/", login_view, name="login"),
    path("personal/crear/", gestionar_personal, name="crear_personal"),
    path("personal/<int:empleado_id>/editar/", gestionar_personal, name="editar_personal"),
    path("personal/<int:user_id>/cambiar-estado/", cambiar_estado_usuario, name="cambiar_estado_usuario"),
    path("perfil/", perfil_usuario, name="perfil_usuario"),
    path("perfil/editar/", editar_perfil, name="editar_perfil"),
    path("perfil/cambiar-contrasena/", cambiar_contrasena, name="cambiar_contrasena"),
]