import sys
import os

# Adding project root to Python path (so Django apps can be found)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow.settings')

import django
django.setup()

from django.test import TestCase, override_settings
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.management import call_command
from io import StringIO
from tasks.models import tasks, ReminderLog
from django.contrib.auth.models import User
from tasks.utils import send_task_reminder_email
from django.core import mail

class ReminderSystemTest(TestCase):
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_send_reminder_email(self):
        """Test that reminder email is sent"""
        task = tasks.objects.create(
            title="Test Task",
            description="Test Description",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        # Send reminder
        send_task_reminder_email(task, self.user)
        
        # Check email was sent
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Reminder', mail.outbox[0].subject)
        self.assertEqual(mail.outbox[0].to[0], 'test@example.com')
    
    @override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_reminder_log_created_on_success(self):
        """Test that log entry is created when email sent successfully"""
        task = tasks.objects.create(
            title="Log Test Task",
            description="Testing logs",
            priority="medium",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        send_task_reminder_email(task, self.user)
        
        # Check log was created
        log = ReminderLog.objects.filter(task=task).first()
        self.assertIsNotNone(log)
        self.assertEqual(log.status, 'sent')
        self.assertEqual(log.recipient_email, 'test@example.com')
    
    def test_command_only_sends_for_tomorrow(self):
        """Test that command only sends reminders for tasks due tomorrow"""
        # Task due tomorrow
        task1 = tasks.objects.create(
            title="Tomorrow Task",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        # Task due today
        task2 = tasks.objects.create(
            title="Today Task",
            priority="high",
            status="pending",
            due_date=timezone.now(),
            user=self.user
        )
        
        # Task due in 3 days
        task3 = tasks.objects.create(
            title="Future Task",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=3),
            user=self.user
        )
        
        # Run command
        call_command('send_reminders')
        
        # Only task1  have a log
        self.assertTrue(ReminderLog.objects.filter(task=task1).exists())
        self.assertFalse(ReminderLog.objects.filter(task=task2).exists())
        self.assertFalse(ReminderLog.objects.filter(task=task3).exists())
    
    def test_dry_run_does_not_send_emails(self):
        """Test that dry run mode doesn't actually send emails"""
        task = tasks.objects.create(
            title="Dry Run Task",
            priority="medium",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        # Run dry run
        call_command('send_reminders', '--dry-run')
        
        # No email should be sent
        self.assertEqual(len(mail.outbox), 0)
        # No log should be created
        self.assertFalse(ReminderLog.objects.filter(task=task).exists())