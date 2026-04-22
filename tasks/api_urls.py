from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import api_views

router = DefaultRouter()
router.register(r'tasks', api_views.TaskViewSet, basename='task')
router.register(r'users', api_views.UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('rest_framework.urls')),
    path('auth/token/', api_views.obtain_auth_token, name='api_token_auth'),
    path('dashboard/stats/', api_views.DashboardStatsView.as_view(), name='dashboard_stats'),
]