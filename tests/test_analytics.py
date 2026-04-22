from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from tasks.models import tasks
from django.utils import timezone
from datetime import timedelta

class AnalyticsTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='analyticsuser',
            password='testpass'
        )
        self.client.login(username='analyticsuser', password='testpass')
        
        # Create various tasks
        tasks.objects.create(
            title="Completed Task",
            status="done",
            priority="high",
            due_date=timezone.now(),
            user=self.user
        )
        tasks.objects.create(
            title="Pending Task",
            status="pending",
            priority="medium",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        tasks.objects.create(
            title="Overdue Task",
            status="pending",
            priority="high",
            due_date=timezone.now() - timedelta(days=1),
            user=self.user
        )
    
    def test_analytics_page_loads(self):
        response = self.client.get(reverse('tasks:analytics'))
        self.assertEqual(response.status_code, 200)
    
    def test_csv_export(self):
        response = self.client.get(reverse('tasks:export_csv'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('attachment', response['Content-Disposition'])
    
    def test_filtered_export(self):
        response = self.client.get(reverse('tasks:export_csv') + '?status=pending')
        content = response.content.decode('utf-8')
        self.assertIn('Pending Task', content)
        self.assertNotIn('Completed Task', content)