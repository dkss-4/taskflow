from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from io import StringIO
from django.contrib.auth.models import User
from .models import tasks  # Your model name is 'tasks'

class ReminderCommandTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
    
    def test_command_finds_due_tasks(self):
        # Create task due tomorrow
        tasks.objects.create(
            title="Due Tomorrow",
            description="Test description",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        out = StringIO()
        call_command('send_reminders', stdout=out)
        
        self.assertIn("Found 1 task(s)", out.getvalue())
    
    def test_command_ignores_completed_tasks(self):
        # Create task due tomorrow but completed
        tasks.objects.create(
            title="Completed Task",
            description="Test description",
            priority="high",
            status="done",  # Status is 'done', not 'completed'
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        out = StringIO()
        call_command('send_reminders', stdout=out)
        
        self.assertIn("No tasks due tomorrow", out.getvalue())
    
    def test_dry_run_mode(self):
        tasks.objects.create(
            title="Test Task",
            description="Test description",
            priority="medium",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        out = StringIO()
        call_command('send_reminders', '--dry-run', stdout=out)
        
        self.assertIn("DRY RUN", out.getvalue())