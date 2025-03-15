from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
import logging

User = get_user_model()


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Customized token serializer that includes additional user info
    and implements extra security measures.
    """
    
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            
            user = self.user
            
            data.update({
                'user_id': user.id,
                'email': user.email,
                'full_name': user.get_full_name(),
                'role': user.role,
                'is_librarian': user.is_librarian,
            })
            
            return data
            
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.error(f"Token validation error: {str(e)}")
            raise


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details."""
    
    is_librarian = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_librarian', 
                 'date_joined', 'is_active')
        read_only_fields = ('id', 'date_joined', 'is_active')


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new user."""
    
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    confirm_password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password', 'confirm_password')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": _("Passwords must match.")})
        
        attrs.pop('confirm_password', None)
        role = attrs.get('role', User.ROLE_PATRON)
        if role not in [User.ROLE_PATRON, User.ROLE_LIBRARIAN]:
            raise serializers.ValidationError({"role": _("Invalid role selected.")})
            
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user