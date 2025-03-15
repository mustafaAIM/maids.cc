from rest_framework import serializers
from .models import Book

class BookSerializer(serializers.ModelSerializer):
    """Serializer for detailed Book representation."""
    
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = [
            'id', 'title', 'author', 'isbn', 'publication_year', 
            'publisher', 'description', 'available_copies', 
            'total_copies', 'is_available', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class BookListSerializer(serializers.ModelSerializer):
    """Serializer for Book list representation with fewer fields."""
    
    is_available = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'publication_year', 'is_available']
