from django.contrib import admin
from .models import tasks

# Register models here.
@admin.register(tasks)
class TaskAdmin(admin.ModelAdmin):
    #What column to be displayed
    list_display = ['title', 'priority', 'status', 'due_date','created_at','updated_at']
    #What field to search
    search_fields = ['title', 'description']
    #What fields to filter by (sidebar)
    list_filter = ['priority', 'status']
    #What fields can be edited directly from list
    list_editable=['priority','status']
    #Date-based navigation
    date_hierarchy = 'due_date'
from .models import ReminderLog

@admin.register(ReminderLog)
class ReminderLogAdmin(admin.ModelAdmin):
    list_display = ['task', 'recipient_email', 'sent_at', 'status']
    list_filter = ['status', 'sent_at']
    search_fields = ['task__title', 'recipient_email']
    readonly_fields = ['sent_at']
