from decimal import Decimal

from django.contrib import messages
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from accounts.models import Empleado
from .forms import FormularioSolicitudTiquete
from .models import ConsumoAlmuerzo, SolicitudTiquete


def consumir_almuerzo_qr(request, codigo_qr):
    empleado = get_object_or_404(Empleado, codigo_qr=codigo_qr, esta_activo=True)

    hoy = timezone.localdate()

    consumo_existente = ConsumoAlmuerzo.objects.filter(
        empleado=empleado,
        fecha=hoy
    ).first()

    if consumo_existente:
        messages.warning(
            request,
            f"El almuerzo de {empleado.usuario.first_name} {empleado.usuario.last_name} ya fue registrado hoy."
        )
    else:
        ConsumoAlmuerzo.objects.create(
            empleado=empleado,
            fecha=hoy
        )
        messages.success(
            request,
            f"Consumo registrado correctamente para {empleado.usuario.first_name} {empleado.usuario.last_name}."
        )

    return render(
        request,
        "schedule/consumo_qr_resultado.html",
        {
            "empleado": empleado,
            "fecha": hoy,
        },
    )


def solicitar_tiquete(request):
    if request.method == "POST":
        formulario = FormularioSolicitudTiquete(request.POST)
        if formulario.is_valid():
            empleado = Empleado.objects.first()

            if not empleado:
                messages.error(request, "No hay empleados registrados para realizar la solicitud.")
                return redirect("solicitar_tiquete")

            solicitud = formulario.save(commit=False)
            solicitud.empleado = empleado
            solicitud.estado = "pendiente"
            solicitud.save()

            messages.success(
                request,
                "La solicitud del tiquete fue enviada correctamente al administrador."
            )
            return redirect("solicitar_tiquete")
    else:
        formulario = FormularioSolicitudTiquete()

    return render(
        request,
        "schedule/solicitar_tiquete.html",
        {"formulario": formulario},
    )


def lista_solicitudes_admin(request):
    solicitudes = SolicitudTiquete.objects.select_related(
        "empleado",
        "empleado__usuario"
    ).order_by("-fecha_solicitud")

    return render(
        request,
        "schedule/lista_solicitudes_admin.html",
        {"solicitudes": solicitudes},
    )


def consultar_estado_cuenta(request, empleado_id):
    empleado = get_object_or_404(Empleado, id=empleado_id, esta_activo=True)

    consumos_pendientes = ConsumoAlmuerzo.objects.filter(
        empleado=empleado,
        pagado=False
    ).order_by("-fecha", "-hora_registro")

    saldo_pendiente = consumos_pendientes.aggregate(
        total=Sum("valor_almuerzo")
    )["total"] or Decimal("0.00")

    total_consumos_pendientes = consumos_pendientes.count()
    ultima_actualizacion = timezone.now()

    return render(
        request,
        "schedule/consultar_estado_cuenta.html",
        {
            "empleado": empleado,
            "consumos_pendientes": consumos_pendientes,
            "saldo_pendiente": saldo_pendiente,
            "total_consumos_pendientes": total_consumos_pendientes,
            "ultima_actualizacion": ultima_actualizacion,
        },
    )
