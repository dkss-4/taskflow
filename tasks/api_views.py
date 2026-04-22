from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import tasks, ReminderLog
from django.contrib.auth.models import User
from .permissions import IsOwnerOrReadOnly
from .serializers import (
    TaskSerializer, UserSerializer, ReminderLogSerializer,
    TaskCreateUpdateSerializer
)

class TaskViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Task CRUD operations
    """
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['priority', 'status']
    search_fields = ['title', 'description']
    ordering_fields = ['due_date', 'priority', 'created_at', 'updated_at']
    ordering = ['due_date']
    
    def get_queryset(self):
        """Only return tasks belonging to the current user"""
        return tasks.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        """Use different serializer for create/update"""
        if self.action in ['create', 'update', 'partial_update']:
            return TaskCreateUpdateSerializer
        return TaskSerializer
    
    def perform_create(self, serializer):
        """Set the user when creating a task"""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as complete"""
        task = self.get_queryset().get(pk=pk)
        task.status = 'done'
        task.save()
        return Response({'status': 'Task marked as complete'})
    
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update task status"""
        task = self.get_queryset().get(pk=pk)
        new_status = request.data.get('status')
        if new_status in ['pending', 'in_progress', 'done']:
            task.status = new_status
            task.save()
            return Response({'status': f'Task status updated to {new_status}'})
        return Response(
            {'error': 'Invalid status'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Get upcoming tasks (due in next 7 days)"""
        upcoming_tasks = self.get_queryset().filter(
            due_date__gte=timezone.now(),
            due_date__lte=timezone.now() + timedelta(days=7),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(upcoming_tasks, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def overdue(self, request):
        """Get overdue tasks"""
        overdue_tasks = self.get_queryset().filter(
            due_date__lt=timezone.now(),
            status__in=['pending', 'in_progress']
        )
        serializer = self.get_serializer(overdue_tasks, many=True)
        return Response(serializer.data)

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing users (read-only)"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only return the current user"""
        return User.objects.filter(id=self.request.user.id)

class DashboardStatsView(APIView):
    """Get dashboard statistics for the current user"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user_tasks = tasks.objects.filter(user=request.user)
        
        stats = {
            'total_tasks': user_tasks.count(),
            'completed_tasks': user_tasks.filter(status='done').count(),
            'pending_tasks': user_tasks.filter(status='pending').count(),
            'in_progress_tasks': user_tasks.filter(status='in_progress').count(),
            'overdue_tasks': user_tasks.filter(
                due_date__lt=timezone.now(),
                status__in=['pending', 'in_progress']
            ).count(),
            'high_priority_tasks': user_tasks.filter(priority='high', status__in=['pending', 'in_progress']).count(),
            'tasks_due_today': user_tasks.filter(
                due_date__date=timezone.now().date(),
                status__in=['pending', 'in_progress']
            ).count(),
        }
        
        # Calculate completion rate
        if stats['total_tasks'] > 0:
            stats['completion_rate'] = round(
                (stats['completed_tasks'] / stats['total_tasks']) * 100, 1
            )
        else:
            stats['completion_rate'] = 0
        
        # Get recent tasks
        recent_tasks = user_tasks.order_by('-created_at')[:5]
        stats['recent_tasks'] = TaskSerializer(recent_tasks, many=True).data
        
        return Response(stats)

class ObtainAuthTokenWithUser(ObtainAuthToken):
    """Custom auth token view that returns user info"""
    
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'email': user.email,
        })

obtain_auth_token = ObtainAuthTokenWithUser.as_view()