from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AuthenticationView,
    UserRegistrationView,
    UserManagementViewSet,
    CustomTokenRefreshView
)

router = DefaultRouter()
router.register('management/users', UserManagementViewSet, basename='user-management')

app_name = 'authentication'

urlpatterns = [
    path('', include(router.urls)),
    path('login/', AuthenticationView.as_view(), name='login'),
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('refresh/',CustomTokenRefreshView.as_view(), name="refresh")
] 