from django.urls import path
from .views import gestionar_personal, perfil_usuario, cambiar_estado_usuario, login_view

urlpatterns = [
    path("login/", login_view, name="login"),
    path("personal/crear/", gestionar_personal, name="crear_personal"),
    path("personal/<int:empleado_id>/editar/", gestionar_personal, name="editar_personal"),
    path("personal/<int:user_id>/cambiar-estado/", cambiar_estado_usuario, name="cambiar_estado_usuario"),
    path("perfil/", perfil_usuario, name="perfil_usuario"),
]
