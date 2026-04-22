import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'taskflow.settings')

import django
django.setup()

from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from django.core.management import call_command
from io import StringIO
from tasks.models import tasks
from django.contrib.auth.models import User

class ReminderCommandTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )
    
    def test_command_finds_due_tasks(self):
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