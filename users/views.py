from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import FormularioPersonal, FormularioPerfilEmpleado
from .models import Empleado, Administrador, Restaurante

User = get_user_model()


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        # Verificar si el usuario existe
        if not User.objects.filter(username=username).exists():
            messages.error(request, "El usuario no existe.")
            return render(request, "registration/login.html")

        # Autenticar usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Iniciar sesión
            login(request, user)

            # Redirigir según rol (Superusuarios siempre van al admin dashboard)
            if user.is_superuser or user.role == 'administrador':
                return redirect("dashboard_admin")
            elif user.role == 'restaurante':
                return redirect("dashboard_restaurante")
            else:  # empleado
                return redirect("dashboard_empleado")
        else:
            # Si el usuario existe pero la contraseña es incorrecta O el usuario está inactivo
            # NOTA: authenticate() devuelve None si el usuario está inactivo (is_active=False)
            user_obj = User.objects.get(username=username)
            if not user_obj.is_active:
                messages.error(request, "Tu cuenta ha sido desactivada. Contacta con administración.")
            else:
                messages.error(request, "Contraseña incorrecta. Por favor intenta de nuevo.")
            return render(request, "registration/login.html")

    return render(request, "registration/login.html")


@login_required
def gestionar_personal(request, empleado_id=None):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        messages.error(request, "No tienes permisos para realizar esta acción.")
        return redirect("dashboard_empleado")

    usuario_editar = get_object_or_404(User, id=empleado_id) if empleado_id else None

    if request.method == "POST":
        formulario = FormularioPersonal(request.POST, instance=usuario_editar)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Personal guardado correctamente.")
            return redirect("dashboard_admin")
    else:
        formulario = FormularioPersonal(instance=usuario_editar)

    return render(
        request,
        "accounts/gestion_personal.html",
        {
            "formulario": formulario,
            "editando": usuario_editar is not None,
            "empleado_user": usuario_editar
        }
    )


@login_required
def perfil_usuario(request):
    """Vista para que cualquier usuario vea sus propios datos de perfil."""
    user = request.user

    context = {
        'view_user': user,
    }
    return render(request, "accounts/perfil.html", context)


@login_required
def editar_perfil(request):
    if request.user.role != 'empleado':
        messages.error(request, "Solo los empleados pueden editar su perfil a través de esta opción.")
        return redirect("perfil_usuario")

    if request.method == "POST":
        formulario = FormularioPerfilEmpleado(request.POST, instance=request.user)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect("perfil_usuario")
    else:
        formulario = FormularioPerfilEmpleado(instance=request.user)

    return render(
        request,
        "accounts/editar_perfil.html",
        {
            "formulario": formulario,
        }
    )


@login_required
def cambiar_estado_usuario(request, user_id):
    """Acción rápida para activar/desactivar un usuario (Solo Admin)."""
    if request.user.role != 'administrador' and not request.user.is_superuser:
        messages.error(request, "Acceso denegado.")
        return redirect("dashboard_empleado")

    user_to_change = get_object_or_404(User, id=user_id)

    # No permitir desactivarse a uno mismo
    if user_to_change == request.user:
        messages.warning(request, "No puedes desactivar tu propia cuenta.")
    else:
        user_to_change.is_active = not user_to_change.is_active
        user_to_change.save()
        estado = "activado" if user_to_change.is_active else "desactivado"
        messages.success(request, f"Usuario {user_to_change.username} {estado} correctamente.")

    return redirect("dashboard_admin")


@login_required
@require_http_methods(["GET", "POST"])
def cambiar_contrasena(request):
    """Permite a cualquier usuario cambiar su contraseña desde su perfil."""
    if request.method == "POST":
        contrasena_actual = request.POST.get("contrasena_actual", "")
        nueva_contrasena = request.POST.get("nueva_contrasena", "")
        confirmar_contrasena = request.POST.get("confirmar_contrasena", "")

        # Validar contraseña actual
        if not request.user.check_password(contrasena_actual):
            messages.error(request, "La contraseña actual es incorrecta.")
            return render(request, "accounts/cambiar_contrasena.html")

        # Validar que las nuevas coincidan
        if nueva_contrasena != confirmar_contrasena:
            messages.error(request, "Las contraseñas nuevas no coinciden.")
            return render(request, "accounts/cambiar_contrasena.html")

        # Validar longitud mínima
        if len(nueva_contrasena) < 8:
            messages.error(request, "La contraseña debe tener al menos 8 caracteres.")
            return render(request, "accounts/cambiar_contrasena.html")

        # Cambiar contraseña y mantener sesión
        request.user.set_password(nueva_contrasena)
        request.user.save()
        update_session_auth_hash(request, request.user)
        messages.success(request, "Tu contraseña ha sido actualizada correctamente.")
        return redirect("perfil_usuario")

    return render(request, "accounts/cambiar_contrasena.html")