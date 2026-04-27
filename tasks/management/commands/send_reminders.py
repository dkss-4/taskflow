from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime, timedelta  # Add 'datetime' here
from tasks.models import tasks
from tasks.utils import send_task_reminder_email
from django.contrib.auth.models import User

class Command(BaseCommand):
    help = 'Send email reminders for tasks due tomorrow'
    
    def add_arguments(self, parser):
        #dry-run argument to test without sending emails
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without actually sending emails',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Calculate tomorrow's date
        tomorrow = timezone.now().date() + timedelta(days=1)
        tomorrow_start = timezone.make_aware(
            datetime.combine(tomorrow, datetime.min.time())
        )
        tomorrow_end = timezone.make_aware(
            datetime.combine(tomorrow, datetime.max.time())
        )
        
        # Find tasks due tomorrow that are not completed
        due_tasks = tasks.objects.filter(
            due_date__range=(tomorrow_start, tomorrow_end),
            status__in=['pending', 'in_progress']  # Only remind for incomplete tasks
        )
        
        count = due_tasks.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS(f'No tasks due tomorrow. No reminders to send.')
            )
            return
        
        self.stdout.write(f'Found {count} task(s) due tomorrow.')
        
        # Send reminders
        reminders_sent = 0
        errors = 0
        
        for task in due_tasks:
            user = task.user
            if not user.email:
                self.stdout.write(
                    self.style.WARNING(f'User {user.username} has no email address. Skipping.')
                )
                continue
            
            if dry_run:
                self.stdout.write(f'[DRY RUN] Would send reminder to {user.email} for task: {task.title}')
                reminders_sent += 1
            else:
                try:
                    send_task_reminder_email(task, user)
                    self.stdout.write(
                        self.style.SUCCESS(f'Reminder sent to {user.email} for task: {task.title}')
                    )
                    reminders_sent += 1
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Failed to send reminder for task {task.id}: {str(e)}')
                    )
                    errors += 1
            
            if not user.email:
                self.stdout.write(
                    self.style.WARNING(f'User {user.username} has no email address. Skipping.')
                )
                # Logged the skip task
                from tasks.models import ReminderLog
                ReminderLog.objects.create(
                    task=task,
                    recipient_email='',
                    status='skipped',
                    error_message=f'User {user.username} has no email address'
                )
                continue
        
        # Summary
        self.stdout.write('=' * 50)
        self.stdout.write(f'Summary: {reminders_sent} reminders sent, {errors} errors')
        
        if dry_run:
            self.stdout.write(self.style.WARNING('This was a DRY RUN. No emails were actually sent.'))
        
