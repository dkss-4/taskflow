from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from .models import ReminderLog 

def send_task_reminder_email(task, user):
    """
    Send a reminder email for a task and log it
    """
    subject = f'Reminder: Task "{task.title}" is due tomorrow'
    
    # Build context for template
    context = {
        'task': task,
        'user': user,
        'site_url': 'http://127.0.0.1:8000',
    }
    
    # Render HTML email
    html_message = render_to_string('tasks/emails/task_reminder.html', context)
    plain_message = render_to_string('tasks/emails/task_reminder.txt', context)
    
    try:
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        # Log success
        ReminderLog.objects.create(
            task=task,
            recipient_email=user.email,
            status='sent'
        )
        return True
        
    except Exception as e:
        # Log failure
        ReminderLog.objects.create(
            task=task,
            recipient_email=user.email,
            status='failed',
            error_message=str(e)
        )
        raise e