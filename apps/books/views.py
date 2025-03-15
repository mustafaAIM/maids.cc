from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from django.utils.translation import gettext_lazy as _
from apps.core.mixins.response_mixins import ResponseMixin
from apps.authentication.permissions import IsLibrarian
from apps.core.aspects.decorators import log_method_call
from apps.core.aspects.decorators import measure_performance
from .models import Book
from .serializers import BookSerializer, BookListSerializer
from .services import BookService
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page 
from django.views.decorators.vary import vary_on_headers


# Create your views here.

class BookViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for Book model.
    Provides CRUD operations with proper permissions and responses.
    """
    queryset = Book.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'list':
            return BookListSerializer
        return BookSerializer
    
    def get_permissions(self):
        """
        Instantiate and return the list of permissions that this view requires.
        Only librarians can create, update or delete books.
        """
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated, IsLibrarian]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
    
    @log_method_call("Book List Request")
    @measure_performance("Book List Performance")
    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(timeout=60 * 5))
    def list(self, request, *args, **kwargs):
        """Get paginated list of books."""
        queryset = self.filter_queryset(self.get_queryset())      
        serializer = self.get_serializer(queryset, many=True)
        return self.send_success_response(
            data=serializer.data,
            message=_("Books retrieved successfully")
        )
    
    @log_method_call("Book Retrieval")
    @measure_performance("Book Retrieval Performance")
    @method_decorator(vary_on_headers('Authorization'))
    @method_decorator(cache_page(timeout=60 * 5))
    def retrieve(self, request, *args, **kwargs):
        """Get a single book by ID."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return self.send_success_response(
            data=serializer.data,
            message=_("Book details retrieved successfully")
        )
    
    @log_method_call("Book Creation")
    @measure_performance("Book Creation Performance")
    def create(self, request, *args, **kwargs):
        """Create a new book."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        book = BookService.create_book(serializer.validated_data)
        
        return self.send_success_response(
            data=BookSerializer(book).data,
            message=_("Book created successfully"),
            status=status.HTTP_201_CREATED
        )
    
    @log_method_call("Book Update")
    @measure_performance("Book Update Performance")
    def update(self, request, *args, **kwargs):
        """Update an existing book."""
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        
        book = BookService.update_book(instance, serializer.validated_data)
        
        return self.send_success_response(
            data=BookSerializer(book).data,
            message=_("Book updated successfully")
        )
    
    @log_method_call("Book Deletion")
    def destroy(self, request, *args, **kwargs):
        """Soft delete a book."""
        instance = self.get_object()
        instance.delete()
        
        return self.send_success_response(
            message=_("Book removed successfully"),
            status=status.HTTP_204_NO_CONTENT
        )
