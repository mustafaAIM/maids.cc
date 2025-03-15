from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import status, viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from apps.core.mixins.response_mixins import ResponseMixin
from .serializers import (
    CustomTokenObtainPairSerializer, 
    UserSerializer, 
    UserCreateSerializer
)
from .permissions import IsLibrarian
from .services import LoginService, UserSecurityService

User = get_user_model()


class AuthenticationView(ResponseMixin, TokenObtainPairView):
    """
    Authentication view for handling login requests.
    Single responsibility: Handle the authentication process.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    def post(self, request, *args, **kwargs):
        email = request.data.get('email', '').lower()
        login_service = LoginService()
        
        try:
            user = User.objects.get(email=email)
            is_locked, minutes = login_service.check_account_locked(user)
            
            if is_locked:
                return self.send_error_response(
                    message=_("Account is locked. Try again in {} minutes.").format(minutes),
                    status=status.HTTP_403_FORBIDDEN
                )
                
        except User.DoesNotExist:
            pass
        
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.user
            token = serializer.validated_data
            ip_address = login_service.get_client_ip(request)
            UserSecurityService.reset_login_attempts(user, ip_address)
            
            return self.send_success_response(
                data=token,
                message=_("Login successful"),
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            if email:
                UserSecurityService.handle_failed_login(email)
            return self.send_error_response(
                message=_("Invalid credentials"),
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserRegistrationView(ResponseMixin, generics.CreateAPIView):
    """
    View for user registration.
    Single responsibility: Handle user registration.
    """
    serializer_class = UserCreateSerializer
    permission_classes = [AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        return self.send_success_response(
            data=UserSerializer(serializer.instance).data,
            message=_("User registered successfully"),
            status=status.HTTP_201_CREATED
        )


class UserManagementViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for user management operations by librarians.
    Single responsibility: Manage users (only accessible to librarians).
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return self.send_success_response(
            data=serializer.data,
            message=_("Users retrieved successfully")
        )
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.send_success_response(
            data=serializer.data,
            message=_("User details retrieved successfully")
        )


class CustomTokenRefreshView(ResponseMixin, TokenRefreshView):
    """
    Custom token refresh view that uses the standard response format.
    Overrides the default TokenRefreshView to use our ResponseMixin.
    """
    def post(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            return self.send_success_response(
                data=serializer.validated_data,
                message="Token refreshed successfully",
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return self.send_error_response(
                message="Token refresh failed",
                errors={"detail": str(e)},
                status=status.HTTP_401_UNAUTHORIZED
            )
