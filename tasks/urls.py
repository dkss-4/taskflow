from django.urls import path
from . import views

app_name = 'tasks'

urlpatterns = [
    # Main pages
    path('', views.task_list, name='task_list'),
    path('register/', views.register, name='register'),
    
    # Task operations
    path('create/', views.task_create, name='task_create'),
    path('<int:pk>/edit/', views.task_edit, name='task_edit'),
    path('<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('<int:pk>/', views.task_detail, name='task_detail'),
    
    # Quick status
    path('quick-status/<int:pk>/<str:status>/', views.quick_status_update, name='quick_status'),
    
    # Analytics & Export
    path('analytics/', views.analytics_dashboard, name='analytics'),
    path('export/csv/', views.export_tasks_csv, name='export_csv'),
    path('api/trigger-reminders/', views.trigger_reminders, name='trigger_reminders'),
    path('setup-admin/', views.setup_initial_admin, name='setup_admin'),
    path('fix-login/', views.fix_admin_login, name='fix_login'),
    
    
]