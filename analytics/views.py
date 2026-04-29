from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import models
from django.db.models import Count, Sum, Q
from django.db.models.functions import TruncDay, TruncMonth, TruncYear
from schedule.models import Consumo, SolicitudTiquete
from users.models import User
import json

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

    context = {
        'chart_data_json': json.dumps(data),
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
