from rest_framework import serializers
from django.contrib.auth.models import User
from .models import tasks, ReminderLog

class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task model"""
    
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    days_until_due = serializers.SerializerMethodField()
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = tasks
        fields = [
            'id', 'title', 'description', 'priority', 'priority_display',
            'status', 'status_display', 'due_date', 'created_at', 'updated_at',
            'days_until_due', 'is_overdue', 'user'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def get_days_until_due(self, obj):
        """Calculate days until due date"""
        from django.utils import timezone
        if obj.due_date:
            delta = obj.due_date - timezone.now()
            return delta.days
        return None
    
    def get_is_overdue(self, obj):
        """Check if task is overdue"""
        from django.utils import timezone
        if obj.due_date and obj.status != 'done':
            return obj.due_date < timezone.now()
        return False

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    task_count = serializers.SerializerMethodField()
    completed_tasks = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'task_count', 'completed_tasks']
        read_only_fields = ['id']
    
    def get_task_count(self, obj):
        return tasks.objects.filter(user=obj).count()
    
    def get_completed_tasks(self, obj):
        return tasks.objects.filter(user=obj, status='done').count()

class ReminderLogSerializer(serializers.ModelSerializer):
    """Serializer for ReminderLog model"""
    
    task_title = serializers.CharField(source='task.title', read_only=True)
    
    class Meta:
        model = ReminderLog
        fields = ['id', 'task', 'task_title', 'sent_at', 'recipient_email', 'status']
        read_only_fields = ['id', 'sent_at']

class TaskCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating tasks with validation"""
    
    class Meta:
        model = tasks
        fields = ['title', 'description', 'priority', 'status', 'due_date']
    
    def validate_due_date(self, value):
        """Validate due date is not in past"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError("Due date cannot be in the past")
        return value