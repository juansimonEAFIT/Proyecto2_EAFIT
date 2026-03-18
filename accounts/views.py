from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormularioPersonal
from .models import Empleado, Administrador, Restaurante

User = get_user_model()

from django.contrib.auth.decorators import login_required

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
