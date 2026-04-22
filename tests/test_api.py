from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth.models import User
from tasks.models import tasks
from django.utils import timezone
from datetime import timedelta

class TaskAPITest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser',
            email='api@test.com',
            password='apipass123'
        )
        self.client.force_authenticate(user=self.user)
        
        self.task = tasks.objects.create(
            title="API Test Task",
            description="Testing API",
            priority="high",
            status="pending",
            due_date=timezone.now() + timedelta(days=1),
            user=self.user
        )
    
    def test_get_tasks_list(self):
        """Test GET /api/tasks/"""
        response = self.client.get('/api/tasks/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_task(self):
        """Test POST /api/tasks/"""
        data = {
            'title': 'New API Task',
            'description': 'Created via API',
            'priority': 'medium',
            'status': 'pending',
            'due_date': (timezone.now() + timedelta(days=2)).isoformat()
        }
        response = self.client.post('/api/tasks/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(tasks.objects.count(), 2)
    
    def test_update_task(self):
        """Test PUT /api/tasks/{id}/"""
        data = {
            'title': 'Updated Task',
            'description': 'Updated via API',
            'priority': 'low',
            'status': 'in_progress',
            'due_date': (timezone.now() + timedelta(days=3)).isoformat()
        }
        response = self.client.put(f'/api/tasks/{self.task.id}/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, 'Updated Task')
    
    def test_delete_task(self):
        """Test DELETE /api/tasks/{id}/"""
        response = self.client.delete(f'/api/tasks/{self.task.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(tasks.objects.count(), 0)
    
    def test_complete_action(self):
        """Test POST /api/tasks/{id}/complete/"""
        response = self.client.post(f'/api/tasks/{self.task.id}/complete/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'done')
    
    def test_upcoming_filter(self):
        """Test GET /api/tasks/upcoming/"""
        response = self.client.get('/api/tasks/upcoming/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_dashboard_stats(self):
        """Test GET /api/dashboard/stats/"""
        response = self.client.get('/api/dashboard/stats/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_tasks', response.data)
        self.assertIn('completion_rate', response.data)

class AuthenticationTest(TestCase):
    
    def test_token_auth(self):
        """Test token authentication"""
        user = User.objects.create_user(
            username='tokenuser',
            password='tokenpass123'
        )
        
        response = self.client.post('/api/auth/token/', {
            'username': 'tokenuser',
            'password': 'tokenpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user_id', response.data)