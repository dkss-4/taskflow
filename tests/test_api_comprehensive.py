from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from tasks.models import tasks
from django.utils import timezone
from datetime import timedelta

class ComprehensiveAPITest(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
    
    def test_task_filtering_by_priority(self):
        tasks.objects.create(
            title="High Priority",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        tasks.objects.create(
            title="Low Priority",
            priority="low",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        response = self.client.get('/api/tasks/?priority=high')
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], "High Priority")
    
    def test_task_search(self):
        tasks.objects.create(
            title="Django Project",
            description="Build a web app",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
        
        response = self.client.get('/api/tasks/?search=Django')
        self.assertEqual(len(response.data['results']), 1)
    
    def test_pagination(self):
        # Create 15 tasks
        for i in range(15):
            tasks.objects.create(
                title=f"Task {i}",
                priority="medium",
                status="pending",
                due_date=timezone.now() + timedelta(days=i),
                user=self.user
            )
        
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data['results']), 10)  # Default page size
        self.assertIsNotNone(response.data['next'])
    
    def test_user_isolation(self):
        # Create another user
        other_user = User.objects.create_user(
            username='other',
            password='otherpass'
        )
        
        # Create task for other user
        tasks.objects.create(
            title="Other User's Task",
            priority="medium",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=other_user
        )
        
        response = self.client.get('/api/tasks/')
        self.assertEqual(len(response.data['results']), 0)