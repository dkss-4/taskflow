from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from .forms import TaskForm
from django.core.paginator import Paginator
import csv
from django.db.models.functions import ExtractWeekDay
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse,JsonResponse
from django.contrib.auth.decorators import login_required
from .models import tasks
import os
from django.core.management import call_command
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Registration View
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('tasks:task_list')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Task List View

@login_required
def task_list(request):
    # Get all tasks for the logged-in user
    task_items = tasks.objects.filter(user=request.user)
    
    # Search functionality
    # The problem: icontains wasn't working with spaces
    # Fixed by using Q objects instead of filter(**kwargs)
    search_query = request.GET.get('search', '')
    if search_query:
        task_items = task_items.filter(
            Q(title__icontains=search_query) | 
            Q(description__icontains=search_query)
        )
    
    # Filter by priority
    priority_filter = request.GET.get('priority', '')
    if priority_filter:
        task_items = task_items.filter(priority=priority_filter)
    
    # Filter by status
    status_filter = request.GET.get('status', '')
    if status_filter:
        task_items = task_items.filter(status=status_filter)
    
    # Sort tasks
    sort_by = request.GET.get('sort', 'due_date')
    task_items = task_items.order_by(sort_by)
    
    # PAGINATION 
    paginator = Paginator(task_items, 10)  # Show 10 tasks per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,  #'page_obj' for pagination
        'search_query': search_query,
        'priority_filter': priority_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'tasks/task_list.html', context)

# Task Create View
@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm()
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Create Task'})

# Task Edit View
@login_required
def task_edit(request, pk):
    task = get_object_or_404(tasks, pk=pk, user=request.user)  
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Task updated successfully!')
            return redirect('tasks:task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'tasks/task_form.html', {'form': form, 'title': 'Edit Task'})

# Task Delete View
@login_required
def task_delete(request, pk):
    task = get_object_or_404(tasks, pk=pk, user=request.user)  
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('tasks:task_list')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

##Task Detail 
@login_required
def task_detail(request, pk):
    task = get_object_or_404(tasks, pk=pk, user=request.user)
    return render(request, 'tasks/task_detail.html', {'task': task})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(tasks, pk=pk, user=request.user)
    
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Task deleted successfully!')
        return redirect('tasks:task_list')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})
@login_required
def quick_status_update(request, pk, status):
    task = get_object_or_404(tasks, pk=pk, user=request.user)
    
    # Validate status is allowed
    valid_statuses = ['pending', 'in_progress', 'done']
    if status in valid_statuses:
        task.status = status
        task.save()
        messages.success(request, f'Task "{task.title}" marked as {task.get_status_display()}')
    else:
        messages.error(request, 'Invalid status')
    
    return redirect('tasks:task_list')


@login_required
def export_tasks_csv(request):
    """Export user's tasks to CSV"""
    
    # Get filter parameters
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    
    # Get tasks for current user
    user_tasks = tasks.objects.filter(user=request.user)
    
    # Apply filters
    if status_filter:
        user_tasks = user_tasks.filter(status=status_filter)
    if priority_filter:
        user_tasks = user_tasks.filter(priority=priority_filter)
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="tasks_export_{timezone.now().date()}.csv"'
    
    writer = csv.writer(response)
    
    # Write headers
    writer.writerow([
        'ID', 'Title', 'Description', 'Priority', 'Status',
        'Due Date', 'Created At', 'Updated At'
    ])
    
    # Write data
    for task in user_tasks:
        writer.writerow([
            task.id,
            task.title,
            task.description,
            task.get_priority_display(),
            task.get_status_display(),
            task.due_date.strftime('%Y-%m-%d %H:%M'),
            task.created_at.strftime('%Y-%m-%d %H:%M'),
            task.updated_at.strftime('%Y-%m-%d %H:%M'),
        ])
    
    return response

@login_required
def analytics_dashboard(request):
    # Get time filter from request
    time_filter = request.GET.get('filter', 'all')
    
    # Start with all user tasks
    user_tasks = tasks.objects.filter(user=request.user)
    
    # Apply time filter based on created_at date
    today = timezone.now().date()
    
    if time_filter == 'week':
        week_ago = today - timedelta(days=7)
        user_tasks = user_tasks.filter(created_at__date__gte=week_ago)
    elif time_filter == 'month':
        month_ago = today - timedelta(days=30)
        user_tasks = user_tasks.filter(created_at__date__gte=month_ago)
    elif time_filter == 'year':
        year_ago = today - timedelta(days=365)
        user_tasks = user_tasks.filter(created_at__date__gte=year_ago)
    
    # Status statistics
    status_stats = {
        'pending': user_tasks.filter(status='pending').count(),
        'in_progress': user_tasks.filter(status='in_progress').count(),
        'done': user_tasks.filter(status='done').count(),
    }
    
    # Priority statistics
    priority_stats = {
        'high': user_tasks.filter(priority='high').count(),
        'medium': user_tasks.filter(priority='medium').count(),
        'low': user_tasks.filter(priority='low').count(),
    }
    
    # Completion rate
    total = user_tasks.count()
    completed = status_stats['done']
    completion_rate = round((completed / total * 100), 1) if total > 0 else 0
    
    #  Tasks created over time
    # Get the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    # Create a list of the last 30 days
    days_list = []
    counts_list = []
    
    for i in range(30):
        date = (timezone.now() - timedelta(days=i)).date()
        days_list.insert(0, date.strftime('%Y-%m-%d'))
        
        # Count tasks created on this date
        count = user_tasks.filter(
            created_at__date=date
        ).count()
        counts_list.insert(0, count)
    
    # Overdue tasks
    overdue_tasks = user_tasks.filter(
        due_date__lt=timezone.now(),
        status__in=['pending', 'in_progress']
    ).count()
    
    # Upcoming tasks (next 7 days)
    upcoming_tasks = user_tasks.filter(
        due_date__gte=timezone.now(),
        due_date__lte=timezone.now() + timedelta(days=7),
        status__in=['pending', 'in_progress']
    ).count()
    
    # Most productive day of week
    tasks_by_weekday = user_tasks.filter(created_at__gte=thirty_days_ago) \
        .annotate(weekday=ExtractWeekDay('created_at')) \
        .values('weekday') \
        .annotate(count=Count('id')) \
        .order_by('-count')
    
    weekday_names = {1: 'Sunday', 2: 'Monday', 3: 'Tuesday', 4: 'Wednesday',
                     5: 'Thursday', 6: 'Friday', 7: 'Saturday'}
    
    most_productive_day = weekday_names.get(
        tasks_by_weekday[0]['weekday'] if tasks_by_weekday else 1,
        'Unknown'
    )
    
    context = {
        'status_stats': status_stats,
        'priority_stats': priority_stats,
        'completion_rate': completion_rate,
        'total_tasks': total,
        'completed_tasks': completed,
        'pending_tasks': status_stats['pending'],
        'overdue_tasks': overdue_tasks,
        'upcoming_tasks': upcoming_tasks,
        'chart_days': days_list,  # Now this is a list of strings
        'chart_counts': counts_list,  # List of integers
        'most_productive_day': most_productive_day,
        'current_filter': time_filter,
    }
    
    return render(request, 'tasks/analytics_dashboard.html', context)




@csrf_exempt
def create_superuser_emergency(request):
    secret = request.GET.get('secret', '')
    if secret == 'CreateAdminNow2026':
        username = 'admin2'
        email = 'dkss.deeksha@gmail.com'
        password = 'Admin2026@Strong'
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            return JsonResponse({'status': 'success', 'message': f'Admin {username} created'})
        else:
            # Reset password
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            return JsonResponse({'status': 'success', 'message': f'Password reset for {username}'})
    return JsonResponse({'status': 'error', 'message': 'Invalid secret'})

@csrf_exempt
def trigger_reminders(request):
    """
    Endpoint to trigger email reminders.
    Called by cron-job.org or GitHub Actions.
    URL: /api/trigger-reminders/?key=YOUR_SECRET_KEY
    """
    # Get the secret key from request or environment
    key = request.GET.get('key', '')
    expected_key = os.getenv('CRON_SECRET_KEY', 'TimeFlyFast')
    
    # Verify the secret key
    if key != expected_key:
        return JsonResponse(
            {'status': 'error', 'message': 'Invalid secret key'},
            status=401
        )
    
    try:
        # Run the send_reminders management command
        call_command('send_reminders')
        return JsonResponse(
            {'status': 'success', 'message': 'Reminders sent successfully'},
            status=200
        )
    except Exception as e:
        return JsonResponse(
            {'status': 'error', 'message': str(e)},
            status=500
        )

from django.contrib.auth.models import User
from django.http import HttpResponse

def reset_admin(request):
    secret = request.GET.get('secret', '')
    if secret == 'ResetAdminNow2026':
        user, created = User.objects.get_or_create(
            username='admin2',
            defaults={
                'email': 'dkss.deeksha@gmail.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        user.set_password('Admin@2026Strong')
        user.save()
        return HttpResponse(f"""
        <h2>✅ Admin Reset Complete</h2>
        <p>Username: <strong>admin2</strong></p>
        <p>Password: <strong>Admin@2026Strong</strong></p>
        <p>Go to <a href="/admin/">/admin/</a> to login</p>
        """)
    return HttpResponse("Invalid secret key")