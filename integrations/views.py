from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
import hashlib

from users.models import Empleado
from schedule.models import InventarioTiquetes, Consumo, SolicitudTiquete

def generar_token_mensual(codigo_qr):
    hoy = timezone.now()
    # Usamos mes y año para que el token cambie cada mes
    mes_year = f"{hoy.month}-{hoy.year}"
    return hashlib.sha256(f"{codigo_qr}{mes_year}".encode()).hexdigest()[:10]

@login_required
def ver_qr_empleado(request):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        return redirect('inicio')
        
    hoy = timezone.now()
    token = generar_token_mensual(empleado.codigo_qr)

    from django.urls import reverse
    url_consumo = request.build_absolute_uri(
        reverse("consumir_almuerzo_qr", kwargs={
            "codigo_qr": empleado.codigo_qr,
            "token": token
        })
    )
    
    # Obtener inventario actual para el límite
    inventario = InventarioTiquetes.objects.filter(mes__month=hoy.month, mes__year=hoy.year).first()
    if not inventario:
        inventario = InventarioTiquetes.objects.order_by("-mes").first()
    
    max_mensual = inventario.max_tiquetes_por_empleado if inventario else 20
    
    # Consumos de ESTE MES
    consumos_mes = Consumo.objects.filter(
        empleado=empleado, 
        fecha_consumo__month=hoy.month, 
        fecha_consumo__year=hoy.year
    ).count()
    
    limite_alcanzado = consumos_mes >= max_mensual
    
    tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").aggregate(total=Sum("cantidad"))["total"] or 0
    tiquetes_consumidos_total = Consumo.objects.filter(empleado=empleado).count()
    tiquetes_disponibles_global = max(0, tiquetes_aprobados - tiquetes_consumidos_total)
    
    return render(
        request, 
        "integrations/qr_empleado.html", # Actualizado el path del template
        {
            "url_consumo": url_consumo,
            "empleado_activo": empleado.esta_activo,
            "tiquetes_disponibles": tiquetes_disponibles_global,
            "limite_alcanzado": limite_alcanzado,
            "consumos_mes": consumos_mes,
            "max_mensual": max_mensual,
        }
    )

@login_required
def consumir_almuerzo_qr(request, codigo_qr, token):
    """
    Vista para registrar consumo de almuerzo mediante QR.
    Ahora incluye validación de token mensual y cuota mensual.
    """
    if request.user.role not in {"restaurante", "administrador"} and not request.user.is_superuser:
        messages.error(request, "Solo el personal autorizado puede registrar consumos por QR.")
        return redirect("inicio")

    # 1. Validar Token Mensual
    token_esperado = generar_token_mensual(codigo_qr)
    if token != token_esperado:
        messages.error(request, "Código QR expirado o no válido para este mes.")
        return render(
            request,
            "integrations/consumo_qr_resultado.html", # Actualizado el path del template
            {"empleado": None, "exito": False, "razon_error": "token_invalido", "fecha": timezone.now()}
        )

    # 2. Buscar empleado
    try:
        empleado = Empleado.objects.get(codigo_qr=codigo_qr)
    except Empleado.DoesNotExist:
        messages.error(request, "Empleado no encontrado.")
        return render(
            request,
            "integrations/consumo_qr_resultado.html",
            {"empleado": None, "exito": False, "razon_error": "empleado_no_existe", "fecha": timezone.now()}
        )
    
    if not empleado.esta_activo:
        messages.error(request, f"El empleado {empleado.user.get_full_name()} está inactivo.")
        return render(
            request,
            "integrations/consumo_qr_resultado.html",
            {"empleado": empleado, "exito": False, "razon_error": "empleado_inactivo", "fecha": timezone.now()}
        )
    
    hoy = timezone.now()
    
    # 3. Validar Cuota Mensual
    inventario = InventarioTiquetes.objects.filter(mes__month=hoy.month, mes__year=hoy.year).first()
    if not inventario:
        inventario = InventarioTiquetes.objects.order_by("-mes").first()
    
    max_mensual = inventario.max_tiquetes_por_empleado if inventario else 20
    consumos_mes = Consumo.objects.filter(
        empleado=empleado, 
        fecha_consumo__month=hoy.month, 
        fecha_consumo__year=hoy.year
    ).count()

    if consumos_mes >= max_mensual:
        messages.error(request, f"El empleado ya alcanzó su límite de {max_mensual} consumos este mes.")
        return render(
            request,
            "integrations/consumo_qr_resultado.html",
            {"empleado": empleado, "exito": False, "razon_error": "limite_mensual_excedido", "fecha": timezone.now()}
        )

    # 4. Validar Tiquetes Disponibles (Global)
    tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").aggregate(total=Sum("cantidad"))["total"] or 0
    tiquetes_consumidos_total = Consumo.objects.filter(empleado=empleado).count()
    tiquetes_disponibles = tiquetes_aprobados - tiquetes_consumidos_total

    # 5. Verificar si ya consumió hoy
    ya_consumio = Consumo.objects.filter(empleado=empleado, fecha_consumo__date=hoy.date()).exists()
    
    if ya_consumio:
        messages.error(request, f"Ya registró su consumo hoy.")
        exito = False
    elif tiquetes_disponibles <= 0:
        messages.error(request, f"No tiene tiquetes disponibles en su saldo.")
        exito = False
    else:
        Consumo.objects.create(empleado=empleado)
        messages.success(request, f"Consumo registrado con éxito para {empleado.user.get_full_name()}.")
        exito = True
    
    return render(
        request, 
        "integrations/consumo_qr_resultado.html", 
        {
            "empleado": empleado,
            "fecha": timezone.now(),
            "exito": exito
        }
    )
