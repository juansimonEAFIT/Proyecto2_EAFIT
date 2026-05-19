from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from schedule.models import Consumo, SolicitudTiquete
from users.models import User
from django.utils import timezone
from datetime import timedelta
import json
from google import genai
from django.core.cache import cache

def is_admin(user):
    return user.is_authenticated and (user.role == 'administrador' or user.is_superuser)

@login_required
@user_passes_test(is_admin)
def analytics_overview(request):
    # Filters
    if request.method == 'POST':
        params = request.POST
    else:
        params = request.GET

    user_search = params.get('user_search', '')
    use_user_filter = params.get('use_user_filter') == 'on'
    
    show_used = params.get('show_used') == 'on'
    show_petitions = params.get('show_petitions') == 'on'
    show_accepted = params.get('show_accepted') == 'on'
    
    # Default behavior: if no metrics selected, show all?
    # Or as per issue: "Admin must be able to see the next graphs by selecting them in a filter menu"
    # So if none selected, we show nothing.
    
    timeframe = params.get('timeframe', 'day') # day, month, year
    
    start_date = params.get('start_date', '')
    end_date = params.get('end_date', '')
    
    export_type = params.get('export_type', '') # csv, excel
    
    x_axis = params.get('x_axis', 'time') # time, count
    y_axis = params.get('y_axis', 'count') # count, time
    
    # Initialize data containers
    data = {
        'labels': [],
        'used': [],
        'petitions': [],
        'accepted': []
    }
    
    # Base Querysets
    consumos_qs = Consumo.objects.all()
    solicitudes_qs = SolicitudTiquete.objects.all()
    
    # Apply Timeframe Boundaries
    if start_date:
        consumos_qs = consumos_qs.filter(fecha_consumo__date__gte=start_date)
        solicitudes_qs = solicitudes_qs.filter(fecha_solicitud__date__gte=start_date)
    if end_date:
        consumos_qs = consumos_qs.filter(fecha_consumo__date__lte=end_date)
        solicitudes_qs = solicitudes_qs.filter(fecha_solicitud__date__lte=end_date)
    
    # Apply User Filter
    if use_user_filter and user_search:
        users = User.objects.filter(
            Q(id__icontains=user_search) | 
            Q(username__icontains=user_search) | 
            Q(email__icontains=user_search)
        )
        consumos_qs = consumos_qs.filter(empleado__user__in=users)
        solicitudes_qs = solicitudes_qs.filter(empleado__user__in=users)
    
    # Time Truncation
    if timeframe == 'year':
        trunc_func = TruncYear
        date_format = '%Y'
    elif timeframe == 'month':
        trunc_func = TruncMonth
        date_format = '%b %Y'
    else:
        trunc_func = TruncDay
        date_format = '%d %b %Y'
        
    # Aggregate Data
    used_stats = consumos_qs.annotate(period=trunc_func('fecha_consumo')).values('period').annotate(total=Count('id')).order_by('period') if show_used else []
    
    # For solicitudes, we might want to distinguish between petitions (all) and accepted (estado='aprobado')
    petitions_stats = solicitudes_qs.annotate(period=trunc_func('fecha_solicitud')).values('period').annotate(total=Sum('cantidad')).order_by('period') if show_petitions else []
    accepted_stats = solicitudes_qs.filter(estado='aprobado').annotate(period=trunc_func('fecha_solicitud')).values('period').annotate(total=Sum('cantidad')).order_by('period') if show_accepted else []

    # Combine all unique periods as labels
    all_periods = set()
    if show_used:
        for item in used_stats:
            if item['period']: all_periods.add(item['period'])
    if show_petitions:
        for item in petitions_stats:
            if item['period']: all_periods.add(item['period'])
    if show_accepted:
        for item in accepted_stats:
            if item['period']: all_periods.add(item['period'])
            
    sorted_periods = sorted(list(all_periods))
    data['labels'] = [p.strftime(date_format) for p in sorted_periods]
    
    # Map data to labels
    used_map = {item['period']: item['total'] for item in used_stats if item['period']}
    petitions_map = {item['period']: item['total'] for item in petitions_stats if item['period']}
    accepted_map = {item['period']: item['total'] for item in accepted_stats if item['period']}
    
    for p in sorted_periods:
        if show_used: data['used'].append(used_map.get(p, 0))
        if show_petitions: data['petitions'].append(petitions_map.get(p, 0))
        if show_accepted: data['accepted'].append(accepted_map.get(p, 0))

    export_type = params.get('export_type', '')
    
    if export_type == 'csv':
        from django.http import HttpResponse
        import csv
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="analiticas_export.csv"'
        response.write('\ufeff') # BOM for Excel
        
        writer = csv.writer(response)
        header = ['Periodo']
        if show_used: header.append('Tiquetes Usados')
        if show_petitions: header.append('Peticiones')
        if show_accepted: header.append('Tiquetes Aceptados')
        writer.writerow(header)
        
        for i, label in enumerate(data['labels']):
            row = [label]
            if show_used: row.append(data['used'][i])
            if show_petitions: row.append(data['petitions'][i])
            if show_accepted: row.append(data['accepted'][i])
            writer.writerow(row)
        return response

    # Calculate Estimated Demand & Insights
    hoy = timezone.now().date()
    hace_30_dias = hoy - timedelta(days=30)
    consumos_recientes = Consumo.objects.filter(fecha_consumo__date__gte=hace_30_dias)
    conteo_por_dia = consumos_recientes.values('fecha_consumo__date').annotate(total=Count('id'))
    
    dias_con_datos = conteo_por_dia.count()
    total_consumos = sum(item['total'] for item in conteo_por_dia) if dias_con_datos > 0 else 0
    estimated_demand = total_consumos / dias_con_datos if dias_con_datos > 0 else 0

    # Smart Insights Logic
    solicitudes_recientes = SolicitudTiquete.objects.filter(fecha_solicitud__date__gte=hace_30_dias, estado='aprobado').aggregate(total=Sum('cantidad'))
    total_solicitudes_recientes = solicitudes_recientes['total'] or 0
    
    used_ratio = total_consumos / total_solicitudes_recientes if total_solicitudes_recientes > 0 else 1.0

    if total_consumos == 0:
        ai_insight = "Recopilando datos... No hay registros suficientes de consumo en los últimos 30 días para generar predicciones."
    elif used_ratio < 0.6:
        ai_insight = f"⚠️ Alerta de Eficiencia: Se han consumido muy pocos tiquetes ({total_consumos}) comparado con los solicitados y aprobados ({total_solicitudes_recientes}). Considera enviar un recordatorio a los empleados o ajustar la cantidad máxima permitida."
    elif used_ratio > 0.95:
        ai_insight = f"🔥 Alta Demanda: El consumo ({total_consumos}) es casi igual a las solicitudes ({total_solicitudes_recientes}). ¡Excelente aprovechamiento de recursos y planificación!"
    else:
        ai_insight = f"📈 Operación Estable: Se estima un volumen constante de {estimated_demand:.1f} almuerzos diarios con una eficiencia de consumo del {used_ratio*100:.0f}%. Todo marcha según lo previsto."

    # --- Integración con Gemini AI con Caché ---
    API_KEY = "AIzaSyBcjbJyUUJN3OZkFi4QVtz7YG1Pxr_ib_M" 
    
    # Creamos una clave única para la caché basada en los datos actuales
    # Si los consumos y el promedio son los mismos, usamos la misma respuesta
    cache_key = f"ai_insight_{total_consumos}_{round(estimated_demand, 1)}"
    cached_insight = cache.get(cache_key)

    if cached_insight:
        ai_insight = cached_insight
    elif API_KEY and API_KEY != "TU_API_KEY_AQUÍ":
        try:
            genai.configure(api_key=API_KEY, transport='rest')
            model = genai.GenerativeModel('gemini-flash-latest')
            
            prompt = f"""
            Actúa como el asistente de Inteligencia Artificial de LunchFlow, una plataforma corporativa de beneficios de almuerzos.
            El usuario que lee esto es el Administrador de Recursos Humanos (RRHH), quien gestiona el presupuesto y la compra de tiquetes para los empleados. NO es el chef ni el dueño del restaurante.
            
            Dale un insight estratégico basado en el uso real del beneficio en los últimos 30 días:
            - Total de tiquetes consumidos por empleados: {total_consumos}
            - Promedio proyectado: {estimated_demand:.1f} tiquetes usados por día
            
            Tu tarea: Dale un consejo administrativo útil sobre la planificación del inventario de tiquetes para el próximo mes o sobre la adopción del sistema por parte de los empleados. 
            Reglas críticas: 
            - NO hables de cocina, ingredientes, comida o preparación. 
            - Enfócate 100% en la gestión administrativa, la compra de tiquetes y el presupuesto de RRHH.
            - Responde en máximo 2 o 3 líneas con un tono profesional, analítico y corporativo.
            """
            response = model.generate_content(prompt)
            ai_insight = response.text.strip()
            
            # Guardamos en caché por 1 hora (3600 segundos)
            cache.set(cache_key, ai_insight, 3600)
            
        except Exception as e:
            # Si falla la IA, no sobreescribimos con el error. 
            # Se queda el mensaje predeterminado (ai_insight) definido arriba.
            pass
    # ---------------------------------

    context = {
        'chart_data_json': json.dumps(data),
        'estimated_demand': estimated_demand,
        'ai_insight': ai_insight,
        'filters': {
            'user_search': user_search,
            'use_user_filter': use_user_filter,
            'show_used': show_used,
            'show_petitions': show_petitions,
            'show_accepted': show_accepted,
            'timeframe': timeframe,
            'start_date': start_date,
            'end_date': end_date,
            'x_axis': x_axis,
            'y_axis': y_axis,
        }
    }
    
    return render(request, 'analytics/analytics_overview.html', context)
