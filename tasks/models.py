from django.db import models
from django.contrib.auth.models import User

class tasks(models.Model):
    PRIORITY_CHOICES=[
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
    ]
    STATUS_CHOICES=[
        ('pending', 'Pending'),
        ('in_progress', 'in_progress'),
        ('done', 'Done'),
    ]

    title=models.CharField(max_length=200)
    description=models.TextField(blank=True)
    # Status and Priority
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='medium'
    )
    status = models.CharField(
        max_length=15,
        choices=STATUS_CHOICES,
        default='pending'
    )
    
    # Dates
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.title

    class Meta:
        ordering=['-due_date']
    
class ReminderLog(models.Model):
    task = models.ForeignKey(tasks, on_delete=models.CASCADE)  
    sent_at = models.DateTimeField(auto_now_add=True)
    recipient_email = models.EmailField()
    status = models.CharField(max_length=20, choices=[
        ('sent', 'Sent'),
        ('failed', 'Failed'),
        ('skipped', 'Skipped'),
    ], default='sent')
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-sent_at']
        verbose_name = 'Reminder Log'
        verbose_name_plural = 'Reminder Logs'

        
    
    def __str__(self):
        return f"Reminder for {self.task.title} sent at {self.sent_at}"
