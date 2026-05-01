import json
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Task
from datetime import date


def dashboard(request):
    today = timezone.now().date()
    all_tasks = Task.objects.all()
    total = all_tasks.count()
    completed = all_tasks.filter(completed=True).count()
    today_tasks = all_tasks.filter(date=today)
    upcoming = all_tasks.filter(date__gt=today, completed=False).count()
    overdue = all_tasks.filter(date__lt=today, completed=False).count()
    progress = round((completed / total * 100) if total > 0 else 0)
    recent_tasks = all_tasks[:5]

    context = {
        'total': total,
        'completed': completed,
        'pending': total - completed,
        'today_tasks': today_tasks,
        'upcoming': upcoming,
        'overdue': overdue,
        'progress': progress,
        'recent_tasks': recent_tasks,
        'today': today,
    }
    return render(request, 'tasks/dashboard.html', context)


def task_list(request):
    filter_type = request.GET.get('filter', 'all')
    today = timezone.now().date()
    tasks = Task.objects.all()

    if filter_type == 'today':
        tasks = tasks.filter(date=today)
    elif filter_type == 'upcoming':
        tasks = tasks.filter(date__gt=today, completed=False)
    elif filter_type == 'completed':
        tasks = tasks.filter(completed=True)
    elif filter_type == 'overdue':
        tasks = tasks.filter(date__lt=today, completed=False)

    counts = {
        'all': Task.objects.count(),
        'today': Task.objects.filter(date=today).count(),
        'upcoming': Task.objects.filter(date__gt=today, completed=False).count(),
        'completed': Task.objects.filter(completed=True).count(),
        'overdue': Task.objects.filter(date__lt=today, completed=False).count(),
    }

    context = {
        'tasks': tasks,
        'filter_type': filter_type,
        'counts': counts,
        'today': today,
    }
    return render(request, 'tasks/task_list.html', context)


def add_task(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        date_str = request.POST.get('date')
        priority = request.POST.get('priority', 'medium')

        if not title:
            messages.error(request, 'Task title is required.')
            return render(request, 'tasks/add_task.html', {'form_data': request.POST})

        try:
            task_date = date.fromisoformat(date_str) if date_str else timezone.now().date()
        except ValueError:
            task_date = timezone.now().date()

        Task.objects.create(
            title=title,
            description=description or None,
            date=task_date,
            priority=priority,
        )
        messages.success(request, f'Task "{title}" added successfully!')
        return redirect('task_list')

    context = {'today': timezone.now().date().isoformat()}
    return render(request, 'tasks/add_task.html', context)


# ── Original toggle (kept for fallback / dashboard forms) ──────────────────
def toggle_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/'))
    return redirect(next_url)


# ── NEW: Fetch API endpoint — returns JSON, no page reload ─────────────────
@require_POST
def toggle_task_ajax(request, task_id):
    """
    Called by the Fetch API in task_list.html.
    Toggles task.completed and returns JSON so the
    frontend can update the UI without reloading the page.
    """
    task = get_object_or_404(Task, id=task_id)
    task.completed = not task.completed
    task.save()

    total = Task.objects.count()
    completed_count = Task.objects.filter(completed=True).count()
    new_progress = round((completed_count / total * 100) if total > 0 else 0)

    return JsonResponse({
        'success': True,
        'task_id': task_id,
        'completed': task.completed,
        'new_progress': new_progress,
        'completed_count': completed_count,
        'total': total,
    })


def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    task.delete()
    messages.success(request, 'Task deleted.')
    next_url = request.POST.get('next', request.META.get('HTTP_REFERER', '/tasks/'))
    return redirect(next_url)


def about(request):
    total = Task.objects.count()
    completed = Task.objects.filter(completed=True).count()
    remaining = total - completed
    progress = round((completed / total * 100) if total > 0 else 0)
    context = {
        'total': total,
        'completed': completed,
        'remaining': remaining,
        'progress': progress,
    }
    return render(request, 'tasks/about.html', context)
