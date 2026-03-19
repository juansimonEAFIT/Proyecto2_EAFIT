from django.contrib import messages
from django.contrib.auth import get_user_model, authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods

from .forms import FormularioPersonal
from .models import Empleado, Administrador, Restaurante

User = get_user_model()




@require_http_methods(["GET", "POST"])
def login_view(request):
    """
    Vista custom de login que valida credenciales y redirige según rol.
    
    Criterios de aceptación:
    - El sistema valida credenciales
    - El usuario accede según su rol
    - Si falla, se muestra un mensaje de error
    """
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        # Autenticar usuario
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Verificar que el usuario esté activo (is_active)
            if not user.is_active:
                messages.error(request, "Tu cuenta ha sido desactivada. Contacta con administración.")
                return render(request, "registration/login.html")
            
            # Iniciar sesión
            login(request, user)
            
            # Redirigir según rol
            if user.role == 'administrador':
                return redirect("dashboard_admin")
            elif user.role == 'restaurante':
                return redirect("dashboard_restaurante")
            else:  # empleado
                return redirect("dashboard_empleado")
        else:
            messages.error(request, "Usuario o contraseña incorrectos. Por favor intenta de nuevo.")
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
    solicitudes = []
    
    if user.role == 'empleado':
        from schedule.models import SolicitudTiquete
        try:
            empleado = user.perfil_empleado
            solicitudes = SolicitudTiquete.objects.filter(empleado=empleado).order_by("-fecha_solicitud")
        except Exception:
            pass
            
    context = {
        'view_user': user,
        'solicitudes': solicitudes,
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
