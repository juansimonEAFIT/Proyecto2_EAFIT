from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import FormularioCreacionEmpleado, FormularioAsignacionRol
from .models import Empleado


def crear_empleado(request):
    if request.method == "POST":
        formulario = FormularioCreacionEmpleado(request.POST)
        if formulario.is_valid():
            with transaction.atomic():
                usuario = User.objects.create_user(
                    username=formulario.cleaned_data["nombre_usuario"],
                    email=formulario.cleaned_data["correo"],
                    password=formulario.cleaned_data["contrasena"],
                    first_name=formulario.cleaned_data["nombre"],
                    last_name=formulario.cleaned_data["apellido"],
                    is_active=True,
                )

                Empleado.objects.create(
                    usuario=usuario,
                    numero_documento=formulario.cleaned_data["numero_documento"],
                    departamento=formulario.cleaned_data["departamento"],
                    telefono=formulario.cleaned_data["telefono"],
                    rol="empleado",
                    esta_activo=True,
                )

            messages.success(
                request,
                "El empleado fue creado correctamente y quedó habilitado para el servicio de almuerzos."
            )
            return redirect("crear_empleado")
    else:
        formulario = FormularioCreacionEmpleado()

    return render(request, "accounts/crear_empleado.html", {"formulario": formulario})


def asignar_rol(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id)

    if request.method == "POST":
        formulario = FormularioAsignacionRol(request.POST, instance=empleado)
        if formulario.is_valid():
            empleado_actualizado = formulario.save()

            if empleado_actualizado.rol == "administrador":
                empleado_actualizado.usuario.is_staff = True
            else:
                empleado_actualizado.usuario.is_staff = False

            empleado_actualizado.usuario.is_active = empleado_actualizado.esta_activo
            empleado_actualizado.usuario.save()

            messages.success(request, "El rol fue actualizado correctamente.")
            return redirect("crear_empleado")
    else:
        formulario = FormularioAsignacionRol(instance=empleado)

    return render(
        request,
        "accounts/asignar_rol.html",
        {
            "formulario": formulario,
            "empleado": empleado,
        },
    )
