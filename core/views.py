from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import redirect, render

from schedule.models import Consumo, InventarioTiquetes, RegistroPago, SolicitudTiquete
from users.models import Empleado

User = get_user_model()


def inicio(request):
    if not request.user.is_authenticated:
        return redirect("login")

    if request.user.role == "administrador" or request.user.is_superuser:
        return redirect("dashboard_admin")

    if request.user.role == "restaurante":
        return redirect("dashboard_restaurante")

    return redirect("dashboard_empleado")


@login_required
def dashboard_empleado(request):
    try:
        empleado = request.user.empleado_perfil
    except Empleado.DoesNotExist:
        if request.user.role == "administrador" or request.user.is_superuser:
            return redirect("dashboard_admin")
        messages.error(request, "No tienes un perfil de empleado asociado.")
        return redirect("login")

    solicitudes = SolicitudTiquete.objects.filter(empleado=empleado).order_by("-fecha_solicitud")[:5]

    # Nueva lógica de saldo: basada en tiquetes comprados (aprobados) vs pagos validados
    from django.db.models import F
    from django.utils import timezone

    month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    tiquetes_aprobados_mes = SolicitudTiquete.objects.filter(
        empleado=empleado,
        estado="aprobado",
        fecha_solicitud__gte=month_start.date(),
    ).aggregate(total=Sum("cantidad"))["total"] or 0

    total_pagos_validados = RegistroPago.objects.filter(
        empleado=empleado,
        validado_por_gh=True,
    ).aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")

    inventario_actual = InventarioTiquetes.objects.order_by("-mes").first()
    precio_tiquete = inventario_actual.precio_tiquete if inventario_actual else Decimal("10000.00")

    # Deuda total basada en el precio al momento de solicitar el tiquete (precio_unitario)
    deuda_total = SolicitudTiquete.objects.filter(
        empleado=empleado,
        estado="aprobado",
    ).annotate(
        costo_total=F("cantidad") * F("precio_unitario")
    ).aggregate(total=Sum("costo_total"))["total"] or Decimal("0.00")

    saldo_pendiente = deuda_total - total_pagos_validados

    tiquetes_consumidos = Consumo.objects.filter(empleado=empleado).count()
    tiquetes_consumidos_mes = Consumo.objects.filter(
        empleado=empleado,
        fecha_consumo__gte=month_start.date(),
    ).count()

    ultimo_consumo = Consumo.objects.filter(empleado=empleado).order_by("-fecha_consumo").first()
    ultimo_consumo_fecha = ultimo_consumo.fecha_consumo.strftime("%d/%m/%Y") if ultimo_consumo else "N/A"

    tiquetes_disponibles = max(0, tiquetes_aprobados_mes - tiquetes_consumidos_mes)

    return render(
        request,
        "core/dashboard_empleado.html",
        {
            "empleado": empleado,
            "solicitudes": solicitudes,
            "saldo_pendiente": f"{saldo_pendiente:,.0f}".replace(",", "."),
            "tiquetes_comprados": tiquetes_aprobados_mes,
            "tiquetes_disponibles": tiquetes_disponibles,
            "tiquetes_consumidos": tiquetes_consumidos,
            "tiquetes_consumidos_mes": tiquetes_consumidos_mes,
            "ultimo_consumo_fecha": ultimo_consumo_fecha,
            "empleado_activo": empleado.esta_activo,
            "precio_tiquete": f"{precio_tiquete:,.0f}".replace(",", "."),
        },
    )


@login_required
def dashboard_restaurante(request):
    if request.user.role != "restaurante" and not request.user.is_superuser:
        return redirect("inicio")

    return render(request, "core/dashboard_restaurante.html")


@login_required
def dashboard_admin(request):
    if request.user.role != "administrador" and not request.user.is_superuser:
        return redirect("dashboard_empleado")

    from django.utils import timezone

    hoy = timezone.localdate()

    # Parámetros de filtro
    mes_str = request.GET.get("mes")
    anio_str = request.GET.get("anio", str(hoy.year))
    empleado_id = request.GET.get("empleado")

    query_kwargs = {}

    if mes_str and anio_str:
        query_kwargs["fecha_solicitud__year"] = int(anio_str)
        query_kwargs["fecha_solicitud__month"] = int(mes_str)

    if empleado_id:
        query_kwargs["empleado_id"] = empleado_id

    solicitudes_historial = SolicitudTiquete.objects.filter(**query_kwargs).order_by("-fecha_solicitud")

    # Si no hay filtros, limitamos a los últimos 50 para no recargar
    if not query_kwargs:
        solicitudes_historial = solicitudes_historial[:50]

    inventario = InventarioTiquetes.objects.order_by("-mes").first()

    # Obtener todo el personal para gestión (Empleados y Restaurantes)
    usuarios_personal = User.objects.filter(role__in=["empleado", "restaurante"]).order_by("first_name")

    from django.db.models import F

    for u in usuarios_personal:
        if u.role == "empleado":
            try:
                emp = u.empleado_perfil
                tiquetes_aprobados = SolicitudTiquete.objects.filter(
                    empleado=emp,
                    estado="aprobado",
                ).annotate(
                    costo_total=F("cantidad") * F("precio_unitario")
                ).aggregate(total=Sum("costo_total"))["total"] or Decimal("0.00")

                total_pagos_validados = RegistroPago.objects.filter(
                    empleado=emp,
                    validado_por_gh=True,
                ).aggregate(total=Sum("valor_pagado"))["total"] or Decimal("0.00")

                u.saldo_pendiente = tiquetes_aprobados - total_pagos_validados
                u.empleado_perfil_id_safe = emp.id
            except Empleado.DoesNotExist:
                u.saldo_pendiente = Decimal("0.00")
                u.empleado_perfil_id_safe = None
        else:
            u.saldo_pendiente = None
            u.empleado_perfil_id_safe = None

    # Solo empleados para el filtro de historial
    solo_empleados = Empleado.objects.select_related("user").all().order_by("user__first_name")

    # Meses para el selector
    meses_opciones = [
        {"id": 1, "nombre": "Enero"},
        {"id": 2, "nombre": "Febrero"},
        {"id": 3, "nombre": "Marzo"},
        {"id": 4, "nombre": "Abril"},
        {"id": 5, "nombre": "Mayo"},
        {"id": 6, "nombre": "Junio"},
        {"id": 7, "nombre": "Julio"},
        {"id": 8, "nombre": "Agosto"},
        {"id": 9, "nombre": "Septiembre"},
        {"id": 10, "nombre": "Octubre"},
        {"id": 11, "nombre": "Noviembre"},
        {"id": 12, "nombre": "Diciembre"},
    ]

    return render(
        request,
        "core/dashboard_admin.html",
        {
            "solicitudes_historial": solicitudes_historial,
            "inventario": inventario,
            "personal": usuarios_personal,
            "solo_empleados": solo_empleados,
            "meses_opciones": meses_opciones,
            "filtro_mes": int(mes_str) if mes_str else None,
            "filtro_anio": int(anio_str),
            "filtro_empleado": int(empleado_id) if empleado_id else None,
        },
    )

