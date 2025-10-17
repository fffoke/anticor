from django.utils import timezone  
from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from web.models import *
from django.contrib import messages
import json
import os
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as auth_login


def main(request):
    if request.method == 'POST':
        login_ = request.POST.get('login')
        password = request.POST.get('password')
        user = authenticate(request,username = login_,password = password)
        if user is not None:
            auth_login(request, user)
            messages.success(request, message='Успешная регистрация')
            return redirect('all_reports/')
        else:
            messages.error(request=request,message='Не верный логин или пороль')
    return render(request, 'main.html')


def all_reports(request, category = None):
    reports = Report.objects.all().order_by('-created_at')
    if category:
        reports = Report.objects.filter(category = category).order_by('-created_at')

    
    return render(request, 'all_reports.html', {'reports': reports})

def sos_page(request):
    # Получаем все SOS сообщения, отсортированные по дате создания (новые сверху)
    sos_messages = Sos.objects.all().order_by('-created_at')
    
    # Статистика с учетом поля is_decided и даты создания
    sos_count = sos_messages.count()
    urgent_count = sos_messages.filter(is_decided=False).count()  # Не решенные = срочные
    today_count = Sos.objects.filter(created_at__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)).count()
    responded_count = sos_messages.filter(is_decided=True).count()  # Решенные
    
    return render(request, 'sos_page.html', {
        'sos_messages': sos_messages,
        'sos_count': sos_count,
        'urgent_count': urgent_count,
        'today_count': today_count,
        'responded_count': responded_count
    })

def sos_stats(request, period=None):
    # Базовая структура для sos_stats (логику добавляйте сами)
    now = timezone.now()
    
    if period == "day":
        start_date = now - timedelta(days=1)
        title = "SOS отчёт за день"
    elif period == "week":
        start_date = now - timedelta(days=7)
        title = "SOS отчёт за неделю"
    elif period == "month":
        start_date = now - timedelta(days=31)
        title = "SOS отчёт за месяц"
    elif period == "year":
        start_date = now - timedelta(days=365)
        title = "SOS отчёт за год"
    else:
        start_date = None
        title = "Все SOS сообщения"
    
    # Получаем SOS сообщения с учетом даты создания
    if start_date:
        sos_messages = Sos.objects.filter(created_at__gte=start_date).order_by('-created_at')
    else:
        sos_messages = Sos.objects.all().order_by('-created_at')
    
    # Статистика с учетом поля is_decided
    total_sos = sos_messages.count()
    active_sos = sos_messages.filter(is_decided=False).count()  # Не решенные = активные
    pending_sos = active_sos  # Не решенные = в ожидании
    processed_sos = sos_messages.filter(is_decided=True).count()  # Решенные
    avg_response_time = 0  # Пока нет поля decided_at в модели
    response_percent = round((processed_sos / total_sos * 100) if total_sos > 0 else 0, 1)
    kazakhstan_sos_count = total_sos
    last_24h_sos = Sos.objects.filter(created_at__gte=now - timedelta(hours=24)).count()
    
    # Получаем координаты SOS для карты с правильными статусами
    sos_with_coords = sos_messages.filter(latitude__isnull=False, longitude__isnull=False)
    sos_coords = []
    for sos in sos_with_coords:
        status = 'PROCESSED' if sos.is_decided else 'ACTIVE'
        sos_coords.append({
            'lat': float(sos.latitude),
            'lon': float(sos.longitude),
            'status': status,
            'name': sos.name,
            'iin': sos.iin,
            'tg_id': sos.tg_id
        })
    
    # Добавляем демо-данные для Казахстана если нет реальных
    if not sos_coords:
        kazakhstan_sos_demo = [
            {'lat': 51.1694, 'lon': 71.4491, 'status': 'ACTIVE', 'name': 'Айдар Нурланов', 'iin': 123456789012, 'tg_id': '@aidar_n'},
            {'lat': 43.2381, 'lon': 76.9456, 'status': 'PENDING', 'name': 'Мария Петрова', 'iin': 234567890123, 'tg_id': '@maria_p'},
            {'lat': 50.4096, 'lon': 80.2277, 'status': 'PROCESSED', 'name': 'Асхат Калиев', 'iin': 345678901234, 'tg_id': '@askhat_k'},
            {'lat': 47.1164, 'lon': 51.9139, 'status': 'ACTIVE', 'name': 'Елена Смирнова', 'iin': 456789012345, 'tg_id': '@elena_s'},
            {'lat': 43.6509, 'lon': 51.1719, 'status': 'PENDING', 'name': 'Нурлан Беков', 'iin': 567890123456, 'tg_id': '@nurlan_b'}
        ]
        sos_coords.extend(kazakhstan_sos_demo)
    
    return render(request, 'sos_stats.html', {
        'title': title,
        'total_sos': total_sos,
        'active_sos': active_sos,
        'pending_sos': pending_sos,
        'processed_sos': processed_sos,
        'avg_response_time': avg_response_time,
        'response_percent': response_percent,
        'kazakhstan_sos_count': kazakhstan_sos_count,
        'last_24h_sos': last_24h_sos,
        'sos_coords': json.dumps(sos_coords),
        'period': period
    })


def report_stats(request, period=None):
    now = timezone.now()

    if period == "day":
        start_date = now - timedelta(days=1)
        title = "Отчёт за день"
    elif period == "week":
        start_date = now - timedelta(days=7)
        title = "Отчет за неделю"
    elif period == "month":
        start_date = now - timedelta(days=31)
        title = "Отчет за месяц"
    elif period == "year":
        start_date = now - timedelta(days=365)
        title = "Отчет за год"
    else:
        start_date = None
        title = "Все жалобы"


    if start_date:
        reposts = Report.objects.filter(created_at__gte=start_date)
    else:
        reposts = Report.objects.all()

    count = reposts.count()
    
    # Подсчитываем категории
    critical_count = reposts.filter(category='CRITICAL').count()
    secondary_count = reposts.filter(category='SECONDARY').count()
    spam_count = reposts.filter(category='SPAM').count()
    
    # Подсчитываем решённые жалобы
    decided_count = reposts.filter(is_decided=True).count()
    resolved_percent = round((decided_count / count * 100) if count > 0 else 0, 1)
    
    # Среднее время обработки (реальный расчёт на основе decided_at)
    decided_reports = reposts.filter(is_decided=True, decided_at__isnull=False)
    if decided_reports.exists():
        total_processing_time = 0
        for report in decided_reports:
            processing_time = report.decided_at - report.created_at
            total_processing_time += processing_time.total_seconds() / 3600  # в часах
        avg_time = round(total_processing_time / decided_reports.count(), 1)
    else:
        avg_time = 0
    
    # Получаем координаты жалоб для карты мира
    reports_with_coords = reposts.filter(latitude__isnull=False, longitude__isnull=False)[:50]  # Ограничиваем до 50 точек
    reports_coords = []
    for report in reports_with_coords:
        reports_coords.append({
            'lat': float(report.latitude),
            'lon': float(report.longitude),
            'category': report.category,
            'title': report.title[:30] + '...' if len(report.title) > 30 else report.title,
            'text': report.text[:100] + '...' if len(report.text) > 100 else report.text,
            'created_at': report.created_at.strftime('%d.%m.%Y %H:%M'),
            'is_decided': report.is_decided
        })
    
    # Добавляем демо-данные для Казахстана если нет реальных данных
    if not reports_coords:
        kazakhstan_demo = [
            {'lat': 51.1694, 'lon': 71.4491, 'category': 'CRITICAL', 'title': 'Коррупция в Нур-Султане', 'text': 'Выявлены факты коррупции в государственных закупках', 'created_at': '15.12.2024 14:30', 'is_decided': False},
            {'lat': 43.2381, 'lon': 76.9456, 'category': 'SECONDARY', 'title': 'Проблемы с дорогами в Алматы', 'text': 'Неудовлетворительное состояние дорожного покрытия', 'created_at': '14.12.2024 09:15', 'is_decided': True},
            {'lat': 50.4096, 'lon': 80.2277, 'category': 'CRITICAL', 'title': 'Злоупотребления в Семее', 'text': 'Нарушения в работе местных органов власти', 'created_at': '13.12.2024 16:45', 'is_decided': False},
            {'lat': 47.1164, 'lon': 51.9139, 'category': 'SECONDARY', 'title': 'Проблемы ЖКХ в Атырау', 'text': 'Отсутствие отопления в многоквартирных домах', 'created_at': '12.12.2024 11:20', 'is_decided': True},
            {'lat': 52.2870, 'lon': 76.9670, 'category': 'SPAM', 'title': 'Ложное сообщение', 'text': 'Неподтвержденная информация', 'created_at': '11.12.2024 08:30', 'is_decided': True},
            {'lat': 43.6509, 'lon': 51.1719, 'category': 'CRITICAL', 'title': 'Коррупция в Актау', 'text': 'Факты взяточничества в портовых службах', 'created_at': '10.12.2024 13:55', 'is_decided': False},
            {'lat': 49.7384, 'lon': 72.6036, 'category': 'SECONDARY', 'title': 'Проблемы образования в Караганде', 'text': 'Нехватка учебных материалов в школах', 'created_at': '09.12.2024 10:10', 'is_decided': True},
            {'lat': 54.8805, 'lon': 69.1542, 'category': 'CRITICAL', 'title': 'Злоупотребления в Петропавловске', 'text': 'Нарушения в распределении социальных выплат', 'created_at': '08.12.2024 15:25', 'is_decided': False}
        ]
        reports_coords.extend(kazakhstan_demo)

    # Дополнительная статистика
    pending_count = reposts.filter(is_decided=False).count()
    kazakhstan_count = len(reports_coords)
    
    # Статистика по времени (последние 24 часа)
    last_24h = reposts.filter(created_at__gte=now - timedelta(hours=24)).count()
    
    # OpenStreetMap не требует API ключа
    
    return render(request , 'report_stats.html', {
        'reposts': reposts,
        'count': count,
        'title': title,
        'critical_count': critical_count,
        'secondary_count': secondary_count,
        'spam_count': spam_count,
        'decided_count': decided_count,
        'pending_count': pending_count,
        'resolved_percent': resolved_percent,
        'avg_time': avg_time,
        'period': period,
        'reports_coords': json.dumps(reports_coords),
        'kazakhstan_count': kazakhstan_count,
        'last_24h_count': last_24h
    })


def is_decided(request, report_id):
    report = Report.objects.get(id=report_id)
    report.is_decided = True
    report.decided_at = timezone.now()
    report.save()
    reports = Report.objects.all()

    return render(request, 'all_reports.html', {'reports': reports})


def sos_decided(request, sos_id):
    """Отметить SOS сообщение как решенное"""
    sos = get_object_or_404(Sos, id=sos_id)
    sos.is_decided = True
    sos.decided_at = timezone.now()
    sos.save()
    messages.success(request, f'SOS сообщение от {sos.name} отмечено как решенное')
    return redirect('web:sos_page')


def decided_reports(request):
    """Отображение решенных жалоб, отсортированных по дате решения (новые сверху)"""
    reports = Report.objects.filter(is_decided=True).order_by('-decided_at')
    return render(request, 'decided_reports.html', {'reports': reports})


def decided_sos(request):
    """Отображение решенных SOS сообщений, отсортированных по дате решения (новые сверху)"""
    sos_messages = Sos.objects.filter(is_decided=True).order_by('-decided_at')
    return render(request, 'decided_sos.html', {'sos_messages': sos_messages})