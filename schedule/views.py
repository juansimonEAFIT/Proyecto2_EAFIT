from decimal import Decimal
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.dateparse import parse_date

from .forms import FormularioSolicitudTiquete, FormularioRegistroPago, FormularioRegistroPagoAdmin, FormularioInventario, FormularioAumentarInventario
from .models import Consumo, SolicitudTiquete, InventarioTiquetes, RegistroPago
from users.models import Empleado, Administrador

# ==========================================
# VISTAS DE EMPLEADO
# ==========================================

@login_required
def solicitar_tiquete(request):
    from django.db import transaction
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        messages.error(request, "Solo los empleados pueden solicitar tiquetes.")
        return redirect("dashboard_empleado")

    # Obtener información básica para mostrar en el formulario (GET o POST fallido)
    hoy = timezone.localdate()
    inventario_info = InventarioTiquetes.objects.filter(mes__month=hoy.month, mes__year=hoy.year).first()
    max_permitido = inventario_info.max_tiquetes_por_empleado if inventario_info else 20
    stock_disponible = inventario_info.cantidad_disponible if inventario_info else 0

    if request.method == "POST":
        formulario = FormularioSolicitudTiquete(request.POST, empleado=empleado)
        if formulario.is_valid():
            cantidad = formulario.cleaned_data["cantidad"]
            solicitud = formulario.save(commit=False)
            solicitud.empleado = empleado

            try:
                with transaction.atomic():
                    # Obtener inventario actual con bloqueo para actualización (para la lógica de aprobación)
                    inventario = InventarioTiquetes.objects.filter(
                        mes__month=hoy.month, mes__year=hoy.year
                    ).select_for_update().first()
                    
                    if not inventario:
                        messages.error(request, "No hay inventario configurado para este periodo.")
                        return render(request, "schedule/solicitar_tiquete.html", {
                            "formulario": formulario,
                            "max_permitido": max_permitido,
                            "stock_disponible": stock_disponible
                        })
                    
                    # Usamos los datos actualizados del bloqueo para la lógica
                    stock_real = inventario.cantidad_disponible
                    limite_real = inventario.max_tiquetes_por_empleado

                    # 1. Validar Inventario Global
                    if cantidad > stock_real:
                        solicitud.estado = "rechazado"
                        solicitud.save()
                        messages.error(request, f"Solicitud rechazada por falta de stock global. (Disponible: {stock_real})")
                        return redirect("dashboard_empleado")
                    
                    # 2. Validar Límite por Empleado
                    tiquetes_ya_aprobados = SolicitudTiquete.objects.filter(
                        empleado=empleado, 
                        estado="aprobado",
                        fecha_solicitud__month=hoy.month,
                        fecha_solicitud__year=hoy.year
                    ).aggregate(total=Sum("cantidad"))["total"] or 0
                    
                    if (tiquetes_ya_aprobados + cantidad) > limite_real:
                        solicitud.estado = "rechazado"
                        solicitud.save()
                        messages.error(request, f"Solicitud rechazada. Has excedido tu límite mensual de {limite_real} tiquetes.")
                        return redirect("dashboard_empleado")

                    # Si todo está bien, aprobamos automáticamente
                    inventario.cantidad_disponible -= cantidad
                    inventario.save()
                    
                    solicitud.estado = "aprobado"
                    solicitud.save()
                    
                    messages.success(request, f"¡Éxito! Tu tiquete ha sido otorgado automáticamente.")
                    return redirect("dashboard_empleado")
            except Exception as e:
                messages.error(request, f"Error al procesar la solicitud: {str(e)}")
                return render(request, "schedule/solicitar_tiquete.html", {
                    "formulario": formulario,
                    "max_permitido": max_permitido,
                    "stock_disponible": stock_disponible
                })
    else:
        formulario = FormularioSolicitudTiquete(empleado=empleado)

    return render(request, "schedule/solicitar_tiquete.html", {
        "formulario": formulario,
        "max_permitido": max_permitido,
        "stock_disponible": stock_disponible
    })


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

    # Filtrado por mes en el historial de compras
    hoy = timezone.localdate()
    try:
        mes_actual = int(request.GET.get('mes', hoy.month))
        anio_actual = int(request.GET.get('anio', hoy.year))
    except ValueError:
        mes_actual = hoy.month
        anio_actual = hoy.year
        
    # Validar rangos de fecha
    if mes_actual < 1 or mes_actual > 12:
        mes_actual = hoy.month
        anio_actual = hoy.year

    # Cálculos para la UI de navegación de meses
    next_month = mes_actual + 1 if mes_actual < 12 else 1
    next_year = anio_actual if mes_actual < 12 else anio_actual + 1
    prev_month = mes_actual - 1 if mes_actual > 1 else 12
    prev_year = anio_actual if mes_actual > 1 else anio_actual - 1
    
    nombres_meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
    mes_nombre = nombres_meses[mes_actual - 1]

    # Historial de compras (tiquetes aprobados) del mes especificado
    compras = SolicitudTiquete.objects.filter(
        empleado=empleado, 
        estado="aprobado",
        fecha_solicitud__year=anio_actual,
        fecha_solicitud__month=mes_actual
    ).order_by("-fecha_solicitud")
    
    # Obtener precio actual del inventario (solo para propósitos informativos generales)
    inventario = InventarioTiquetes.objects.order_by("-mes").first()
    precio_tiquete = inventario.precio_tiquete if inventario else Decimal("10000.00")

    # Calcular valor detallado usando el precio histórico grabado (precio_unitario)
    for compra in compras:
        compra.valor_total = compra.cantidad * getattr(compra, 'precio_unitario', Decimal('10000.00'))
        
    # Historial de pagos validados
    pagos = RegistroPago.objects.filter(empleado=empleado, validado_por_gh=True).order_by("-fecha_pago")
    
    tiquetes_aprobados = compras.aggregate(total=Sum("cantidad"))["total"] or 0
    tiquetes_consumidos = Consumo.objects.filter(
        empleado=empleado, 
        fecha_consumo__month=mes_actual,
        fecha_consumo__year=anio_actual
    ).count()
    tiquetes_disponibles = max(0, tiquetes_aprobados - tiquetes_consumidos)
    
    total_pagos_validados = pagos.aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")
    
    from django.db.models import F
    deuda_total = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").annotate(
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
            "mes_nombre": mes_nombre,
            "anio_actual": anio_actual,
            "prev_month": prev_month,
            "prev_year": prev_year,
            "next_month": next_month,
            "next_year": next_year,
        },
    )

@login_required
def confirmar_pago_empleado(request, pago_id):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        return redirect("dashboard_empleado")

    pago = get_object_or_404(RegistroPago, id=pago_id, empleado=empleado)
    pago.confirmado_por_empleado = True
    pago.save()
    messages.success(request, f"Pago de ${pago.valor_pagado:.0f} confirmado exitosamente.")
    return redirect("consultar_estado_cuenta")


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
def registrar_pago_efectivo(request):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    if request.method == "POST":
        formulario = FormularioRegistroPagoAdmin(request.POST)
        if formulario.is_valid():
            pago = formulario.save(commit=False)
            pago.validado_por_gh = True
            pago.confirmado_por_empleado = False
            pago.comprobante = "Pago en efectivo (Caja RRHH)"
            pago.save()
            messages.success(request, f"Pago de ${pago.valor_pagado:.0f} registrado para {pago.empleado.user.get_full_name() or pago.empleado.user.username}.")
            return redirect("dashboard_admin")
    else:
        formulario = FormularioRegistroPagoAdmin()

    return render(request, "schedule/registrar_pago_efectivo.html", {"formulario": formulario})


@login_required
def gestionar_inventario(request):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    hoy = timezone.now()
    # Buscar si ya existe un inventario para este mes y año
    inventario = InventarioTiquetes.objects.filter(
        mes__month=hoy.month, 
        mes__year=hoy.year
    ).first()
    
    # Si no hay uno para este mes, buscar el último de meses anteriores para precargar datos
    if not inventario:
        ultimo_global = InventarioTiquetes.objects.order_by("-mes").first()
        if ultimo_global:
            from datetime import date
            instancia_inicial = InventarioTiquetes(
                mes=date(hoy.year, hoy.month, 1),
                cantidad_inicial=ultimo_global.cantidad_inicial,
                max_tiquetes_por_empleado=ultimo_global.max_tiquetes_por_empleado,
                precio_tiquete=ultimo_global.precio_tiquete
            )
        else:
            instancia_inicial = None
    else:
        instancia_inicial = inventario

    ya_existe = inventario is not None

    if request.method == "POST":
        formulario = FormularioInventario(request.POST, instance=instancia_inicial, ya_existe=ya_existe)
        if formulario.is_valid():
            inv = formulario.save(commit=False)
            
            # Si es una creación nueva para el mes
            if not ya_existe:
                inv.cantidad_disponible = inv.cantidad_inicial
                inv.save()
                messages.success(request, f"Inventario para {inv.mes.strftime('%B %Y')} configurado con éxito.")
            else:
                inv.save()
                messages.success(request, "Límites y precios actualizados correctamente.")
            
            return redirect("dashboard_admin")
    else:
        # Si es nuevo mes, pasamos los valores del último pero sin ser la misma instancia de DB
        formulario = FormularioInventario(instance=instancia_inicial, ya_existe=ya_existe)

    form_aumentar = FormularioAumentarInventario() if ya_existe else None

    return render(request, "schedule/gestionar_inventario.html", {
        "formulario": formulario,
        "ya_existe": ya_existe,
        "inventario": inventario,
        "form_aumentar": form_aumentar,
    })


@login_required
def aumentar_inventario(request):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    if request.method == "POST":
        inventario = InventarioTiquetes.objects.order_by("-mes").first()
        if not inventario:
            messages.error(request, "No hay un inventario configurado para aumentar.")
            return redirect("gestionar_inventario")

        form = FormularioAumentarInventario(request.POST)
        if form.is_valid():
            adicion = form.cleaned_data["cantidad_a_adicionar"]
            inventario.cantidad_disponible += adicion
            inventario.cantidad_inicial += adicion # También aumentamos el total del mes para reportes
            inventario.save()
            messages.success(request, f"Se han adicionado {adicion} tiquetes al inventario. Nuevo stock disponible: {inventario.cantidad_disponible}")
        else:
            messages.error(request, "La cantidad a adicionar no es válida.")

    return redirect("gestionar_inventario")


@login_required
def historial_consumos(request, empleado_id):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    consumos = Consumo.objects.filter(
        empleado_id=empleado_id
    ).order_by('-fecha_consumo')

    return render(request, "schedule/historial_consumo.html", {
        "consumos": consumos
    })


@login_required
def historial_consumos_restaurante(request):
    """Muestra los consumos registrados en una fecha específica (por defecto hoy) por el restaurante."""
    if request.user.role != 'restaurante' and not request.user.is_superuser:
        return redirect("inicio")

    hoy = timezone.localdate()
    fecha_filtro = hoy
    es_hoy = True

    fecha_str = request.GET.get('fecha')
    if fecha_str:
        parsed_date = parse_date(fecha_str)
        if parsed_date:
            fecha_filtro = parsed_date
            es_hoy = (parsed_date == hoy)

    consumos_hoy = Consumo.objects.filter(
        fecha_consumo__date=fecha_filtro
    ).select_related(
        'empleado__user'
    ).order_by('-fecha_consumo')

    return render(request, "schedule/historial_consumos_restaurante.html", {
        "consumos_hoy": consumos_hoy,
        "total_consumos_hoy": consumos_hoy.count(),
        "fecha_filtro": fecha_filtro,
        "es_hoy": es_hoy,
    })
