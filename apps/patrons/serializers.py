from rest_framework import serializers
from .models import Patron


class PatronSerializer(serializers.ModelSerializer):
    """Serializer for Patron model"""
    full_name = serializers.CharField(read_only=True)
    has_active_loans = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Patron
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 
            'phone_number', 'address', 'birth_date', 'membership_date', 
            'active', 'member_id', 'has_active_loans', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'membership_date']
    
    def validate_email(self, value):
        """Validate email is unique"""
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
            
        if Patron.objects.filter(email=value).exists():
            raise serializers.ValidationError("A patron with this email already exists.")
        return value
        
    def validate_member_id(self, value):
        """Validate member_id is unique"""
        instance = getattr(self, 'instance', None)
        if instance and instance.member_id == value:
            return value
            
        if Patron.objects.filter(member_id=value).exists():
            raise serializers.ValidationError("A patron with this member ID already exists.")
        return value