from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import FormularioSolicitudTiquete, FormularioRegistroPago, FormularioInventario
from .models import Consumo, SolicitudTiquete, InventarioTiquetes, RegistroPago, Schedule, ComidaReservada
from users.models import Empleado, Administrador

from django.http import JsonResponse
from django.core.exceptions import ValidationError

# ==========================================
# VISTAS DE EMPLEADO
# ==========================================

@login_required
def solicitar_tiquete(request):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        messages.error(request, "Solo los empleados pueden solicitar tiquetes.")
        return redirect("dashboard_empleado")

    inventario = InventarioTiquetes.objects.order_by("-mes").first()
    max_permitido = inventario.max_tiquetes_por_empleado if inventario else 20
    stock_disponible = inventario.cantidad_disponible if inventario else 0

    if request.method == "POST":
        formulario = FormularioSolicitudTiquete(request.POST, empleado=empleado)
        if formulario.is_valid():
            cantidad = formulario.cleaned_data["cantidad"]
            
            # 1. Validar Inventario Global
            if cantidad > stock_disponible:
                messages.error(request, f"No hay suficientes tiquetes en inventario. Disponibles: {stock_disponible}")
                return render(request, "schedule/solicitar_tiquete.html", {"formulario": formulario})
            
            # 2. Validar Límite por Empleado (Aprobados + Pendientes + Nueva solicitud)
            tiquetes_ya_usados = SolicitudTiquete.objects.filter(
                empleado=empleado, 
                estado__in=["pendiente", "aprobado"]
            ).aggregate(total=Sum("cantidad"))["total"] or 0
            
            if (tiquetes_ya_usados + cantidad) > max_permitido:
                quedan = max(0, max_permitido - tiquetes_ya_usados)
                messages.error(request, f"Has excedido tu límite mensual de {max_permitido} tiquetes. Solo puedes pedir {quedan} más.")
                return render(request, "schedule/solicitar_tiquete.html", {"formulario": formulario})

            solicitud = formulario.save(commit=False)
            solicitud.empleado = empleado
            solicitud.save()
            messages.success(request, "Solicitud enviada correctamente.")
            return redirect("dashboard_empleado")
    else:
        formulario = FormularioSolicitudTiquete(empleado=empleado)

    return render(request, "schedule/solicitar_tiquete.html", {"formulario": formulario})


@login_required
def registrar_pago(request):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        return redirect("dashboard_empleado")

    if request.method == "POST":
        formulario = FormularioRegistroPago(request.POST)
        if formulario.is_valid():
            pago = formulario.save(commit=False)
            pago.empleado = empleado
            pago.save()
            messages.success(request, "Pago registrado. Pendiente de validación por Gestión Humana.")
            return redirect("dashboard_empleado")
    else:
        formulario = FormularioRegistroPago()

    return render(request, "schedule/registrar_pago.html", {"formulario": formulario})


@login_required
def consultar_estado_cuenta(request):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        return redirect("dashboard_empleado")

    # Historial de compras (tiquetes aprobados)
    compras = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").order_by("-fecha_solicitud")
    
    # Obtener precio actual del inventario (solo para propósitos informativos generales)
    inventario = InventarioTiquetes.objects.order_by("-mes").first()
    precio_tiquete = inventario.precio_tiquete if inventario else Decimal("10000.00")

    # Calcular valor detallado usando el precio histórico grabado (precio_unitario)
    for compra in compras:
        compra.valor_total = compra.cantidad * getattr(compra, 'precio_unitario', Decimal('10000.00'))
        
    # Historial de pagos validados
    pagos = RegistroPago.objects.filter(empleado=empleado, validado_por_gh=True).order_by("-fecha_pago")
    
    tiquetes_aprobados = compras.aggregate(total=Sum("cantidad"))["total"] or 0
    tiquetes_consumidos = Consumo.objects.filter(comida__empleado=empleado).count()
    tiquetes_disponibles = max(0, tiquetes_aprobados - tiquetes_consumidos)
    
    total_pagos_validados = pagos.aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")
    
    from django.db.models import F
    deuda_total = compras.annotate(
        costo_total=F('cantidad') * F('precio_unitario')
    ).aggregate(total=Sum('costo_total'))["total"] or Decimal("0.00")
    
    saldo_pendiente = deuda_total - total_pagos_validados

    return render(
        request,
        "schedule/consultar_estado_cuenta.html",
        {
            "empleado": empleado,
            "compras": compras,
            "pagos": pagos,
            "saldo_pendiente": saldo_pendiente,
            "tiquetes_comprados": tiquetes_aprobados,
            "tiquetes_disponibles": tiquetes_disponibles,
            "precio_tiquete": precio_tiquete,
            "ultima_actualizacion": timezone.now(),
        },
    )


@login_required
def ver_qr_empleado(request):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        return redirect('inicio')
        
    from django.urls import reverse
    url_consumo = request.build_absolute_uri(
        reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr})
    )
    
    tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").aggregate(total=Sum("cantidad"))["total"] or 0
    tiquetes_consumidos = Consumo.objects.filter(comida__empleado=empleado).count()
    tiquetes_disponibles = max(0, tiquetes_aprobados - tiquetes_consumidos)
    
    return render(
        request, 
        "schedule/qr_empleado.html", 
        {
            "url_consumo": url_consumo,
            "empleado_activo": empleado.esta_activo,
            "tiquetes_disponibles": tiquetes_disponibles,
        }
    )

@login_required
def consumir_comida(request, comida_id):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        return redirect('inicio')

    # Solo permitir POST
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    comida = get_object_or_404(ComidaReservada, id=comida_id)

    # Obtener schedule del empleado dueño de la comida
    try:
        schedule = Schedule.objects.get(empleado=comida.empleado)
    except Schedule.DoesNotExist:
        return JsonResponse({"error": "El empleado no tiene schedule asociado"}, status=400)

    # Intentar consumir usando la lógica del modelo
    try:
        consumo = schedule.consumir(comida)
        return JsonResponse({
            "status": "ok",
            "mensaje": "Consumo registrado correctamente",
            "consumo_id": consumo.id,
            "empleado": str(consumo.comida.empleado),
            "comida": consumo.comida.comida.nombre,
            "fecha_consumo": consumo.fecha_consumo,
        })
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)


# ==========================================
# VISTAS DE RESTAURANTE
# ==========================================

@login_required
def consumir_almuerzo_qr(request, codigo_qr):
    """
    Vista para registrar consumo de almuerzo mediante QR.
    
    Criterios de aceptación (Historia 2):
    - Solo empleados activos pueden consumir
    - Si está inactivo, el sistema bloquea el registro
    - Se muestra un mensaje claro
    """
    if request.user.role not in {"restaurante", "administrador"} and not request.user.is_superuser:
        messages.error(request, "Solo el personal autorizado puede registrar consumos por QR.")
        return redirect("inicio")

    # Buscar empleado por QR (activo o inactivo)
    try:
        empleado = Empleado.objects.get(codigo_qr=codigo_qr)
    except Empleado.DoesNotExist:
        messages.error(request, "Código QR no válido. Empleado no encontrado.")
        return render(
            request,
            "schedule/consumo_qr_resultado.html",
            {"empleado": None, "exito": False, "razon_error": "empleado_no_existe", "fecha": timezone.now()}
        )
    
    # Validar que el empleado esté activo
    if not empleado.esta_activo:
        messages.error(
            request,
            f"Acceso denegado. El empleado {empleado.user.get_full_name()} está inactivo. "
            "Contacta con gestión humana para reactivar tu cuenta."
        )
        return render(
            request,
            "schedule/consumo_qr_resultado.html",
            {"empleado": empleado, "exito": False, "razon_error": "empleado_inactivo", "fecha": timezone.now()}
        )
    
    hoy = timezone.localdate()
    
    # 1. Calcular tiquetes disponibles
    tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").aggregate(total=Sum("cantidad"))["total"] or 0
    tiquetes_consumidos = Consumo.objects.filter(comida__empleado=empleado).count()
    tiquetes_disponibles = tiquetes_aprobados - tiquetes_consumidos

    # 2. Verificar si ya consumió hoy
    ya_consumio = Consumo.objects.filter(comida__empleado=empleado, fecha_consumo__date=hoy).exists()
    
    if ya_consumio:
        messages.error(request, f"El empleado {empleado.user.get_full_name()} ya registró su consumo hoy.")
        exito = False
    elif tiquetes_disponibles <= 0:
        messages.error(request, f"Consumo denegado. El empleado {empleado.user.get_full_name()} no tiene tiquetes disponibles.")
        exito = False
    else:
        # Para registrar el consumo vía QR, necesitamos una ComidaReservada (Almuerzo) para este empleado.
        # Si no existe reserva hoy, intentamos buscar una o crear una genérica para poder registrar el consumo.
        comida_hoy = ComidaReservada.objects.filter(empleado=empleado, fecha_de_consumo=hoy).first()
        
        if not comida_hoy:
            # Intentar obtener una comida base para crear la reserva
            from .models import Comida
            comida_base = Comida.objects.order_by("-fecha_de_creacion").first()
            if not comida_base:
                # Si ni siquiera hay comidas definidas, no podemos registrar el consumo
                messages.error(request, "No hay comidas configuradas en el sistema para registrar el consumo.")
                return render(
                    request,
                    "schedule/consumo_qr_resultado.html",
                    {"empleado": empleado, "exito": False, "razon_error": "sin_comidas", "fecha": timezone.now()},
                )
            
            comida_hoy = ComidaReservada.objects.create(
                empleado=empleado,
                comida=comida_base,
                fecha_de_consumo=hoy,
                tipo="almuerzo"
            )

        Consumo.objects.create(
            comida=comida_hoy
        )
        messages.success(request, f"Consumo registrado con éxito para {empleado.user.get_full_name()}.")
        exito = True
    
    return render(
        request, 
        "schedule/consumo_qr_resultado.html", 
        {
            "empleado": empleado,
            "fecha": timezone.now(),
            "exito": exito
        }
    )


# ==========================================
# VISTAS DE ADMINISTRADOR
# ==========================================

@login_required
def gestionar_solicitud(request, solicitud_id, accion):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    solicitud = get_object_or_404(SolicitudTiquete, id=solicitud_id)
    if accion == "aprobar":
        inventario = InventarioTiquetes.objects.order_by("-mes").first()
        if inventario and inventario.cantidad_disponible >= solicitud.cantidad:
            inventario.cantidad_disponible -= solicitud.cantidad
            inventario.save()
            solicitud.estado = "aprobado"
            messages.success(request, f"Solicitud de {solicitud.empleado} aprobada e inventario actualizado.")
        else:
            messages.error(request, "No hay suficiente inventario para aprobar esta solicitud.")
            return redirect("dashboard_admin")
    elif accion == "rechazar":
        solicitud.estado = "rechazado"
        messages.info(request, f"Solicitud de {solicitud.empleado} rechazada.")
    
    solicitud.save()
    return redirect("dashboard_admin")


@login_required
def gestionar_pago(request, pago_id):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    pago = get_object_or_404(RegistroPago, id=pago_id)
    pago.validado_por_gh = True
    pago.save()

    # Actualizar consumos como pagados para este empleado
    # Nota: Consumo no tiene campo 'pagado', se asume que la validación del pago es suficiente
    # para el saldo global del empleado.
    # Consumo.objects.filter(comida__empleado=pago.empleado).update(pagado=True)
    
    messages.success(request, f"Pago de {pago.empleado} validado y saldo actualizado.")
    return redirect("dashboard_admin")


@login_required
def gestionar_inventario(request):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    # Obtener el inventario del mes actual o crear uno básico si no existe
    inventario = InventarioTiquetes.objects.order_by("-mes").first()
    
    if request.method == "POST":
        formulario = FormularioInventario(request.POST, instance=inventario)
        if formulario.is_valid():
            inv = formulario.save(commit=False)
            # Al actualizar el inicial, si es nuevo o reinicio, actualizamos el disponible
            if not inventario or 'cantidad_inicial' in formulario.changed_data:
                inv.cantidad_disponible = inv.cantidad_inicial
            inv.save()
            messages.success(request, "Inventario y límites actualizados correctamente.")
            return redirect("dashboard_admin")
    else:
        formulario = FormularioInventario(instance=inventario)

    return render(request, "schedule/gestionar_inventario.html", {"formulario": formulario})


@login_required
def historial_consumos(request, empleado_id):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    consumos = Consumo.objects.filter(
        comida__empleado_id=empleado_id
    ).order_by('-fecha_consumo')

    return render(request, "schedule/historial_consumo.html", {
        "consumos": consumos
    })
