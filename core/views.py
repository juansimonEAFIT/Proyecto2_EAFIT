from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum
from django.contrib.auth import get_user_model
from schedule.models import SolicitudTiquete, RegistroPago, ConsumoAlmuerzo, InventarioTiquetes
from accounts.models import Empleado

User = get_user_model()


def inicio(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.user.role == 'administrador' or request.user.is_superuser:
        return redirect('dashboard_admin')
    
    if request.user.role == 'restaurante':
        return redirect('dashboard_restaurante')
    
    return redirect('dashboard_empleado')


@login_required
def dashboard_empleado(request):
    try:
        empleado = request.user.perfil_empleado
    except Empleado.DoesNotExist:
        if request.user.role == 'administrador' or request.user.is_superuser:
            return redirect('dashboard_admin')
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect("login")

    solicitudes = SolicitudTiquete.objects.filter(empleado=empleado).order_by("-fecha_solicitud")[:5]
    
    # Nueva lógica de saldo: Basada en tiquetes comprados (aprobados) vs pagos validados
    from django.db.models import F
    tiquetes_aprobados = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").aggregate(total=Sum("cantidad"))["total"] or 0
    total_pagos_validados = RegistroPago.objects.filter(empleado=empleado, validado_por_gh=True).aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")
    
    inventario_actual = InventarioTiquetes.objects.order_by("-mes").first()
    precio_tiquete = inventario_actual.precio_tiquete if inventario_actual else Decimal("10000.00")
    
    # Deuda total basada en el precio al momento de solicitar el tiquete (precio_unitario)
    deuda_total = SolicitudTiquete.objects.filter(empleado=empleado, estado="aprobado").annotate(
        costo_total=F('cantidad') * F('precio_unitario')
    ).aggregate(total=Sum('costo_total'))["total"] or Decimal("0.00")
    
    saldo_pendiente = deuda_total - total_pagos_validados
    
    from django.utils import timezone
    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    tiquetes_consumidos = ConsumoAlmuerzo.objects.filter(empleado=empleado).count()
    tiquetes_consumidos_mes = ConsumoAlmuerzo.objects.filter(empleado=empleado, fecha__gte=month_start.date()).count()
    
    ultimo_consumo = ConsumoAlmuerzo.objects.filter(empleado=empleado).order_by("-fecha").first()
    ultimo_consumo_fecha = ultimo_consumo.fecha.strftime("%d/%m/%Y") if ultimo_consumo else "N/A"
    
    tiquetes_disponibles = max(0, tiquetes_aprobados - tiquetes_consumidos)

    # URL para el código QR (Solución ingeniosa)
    from django.urls import reverse
    url_consumo = request.build_absolute_uri(
        reverse("consumir_almuerzo_qr", kwargs={"codigo_qr": empleado.codigo_qr})
    )

    return render(
        request,
        "core/dashboard_empleado.html",
        {
            "empleado": empleado,
            "solicitudes": solicitudes,
            "saldo_pendiente": f"{saldo_pendiente:,.0f}".replace(",", "."),
            "tiquetes_comprados": tiquetes_aprobados,
            "tiquetes_disponibles": tiquetes_disponibles,
            "tiquetes_consumidos": tiquetes_consumidos,
            "tiquetes_consumidos_mes": tiquetes_consumidos_mes,
            "ultimo_consumo_fecha": ultimo_consumo_fecha,
            "url_consumo": url_consumo,
            "empleado_activo": empleado.esta_activo,
            "precio_tiquete": f"{precio_tiquete:,.0f}".replace(",", "."),
        },
    )


@login_required
def dashboard_restaurante(request):
    if request.user.role != 'restaurante' and not request.user.is_superuser:
        return redirect("inicio")
        
    return render(request, "core/dashboard_restaurante.html")


@login_required
def dashboard_admin(request):
    if request.user.role != 'administrador' and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    solicitudes_pendientes = SolicitudTiquete.objects.filter(estado="pendiente").order_by("-fecha_solicitud")
    solicitudes_historial = SolicitudTiquete.objects.exclude(estado="pendiente").order_by("-fecha_solicitud")[:10]
    pagos_pendientes = RegistroPago.objects.filter(validado_por_gh=False).order_by("-fecha_pago")
    inventario = InventarioTiquetes.objects.order_by("-mes").first()
    # Obtener todo el personal (Empleados y Restaurantes)
    usuarios_personal = User.objects.filter(role__in=['empleado', 'restaurante']).order_by("last_name")

    return render(
        request,
        "core/dashboard_admin.html",
        {
            "solicitudes_pendientes": solicitudes_pendientes,
            "solicitudes_historial": solicitudes_historial,
            "pagos_pendientes": pagos_pendientes,
            "inventario": inventario,
            "personal": usuarios_personal,
        },
    )
