from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from apps.core.aspects.decorators import log_method_call
from .models import Book

class BookService:
    """
    Service class for Book-related business logic.
    Follows Single Responsibility and Dependency Inversion principles.
    """
    
    @staticmethod
    @log_method_call()
    def validate_isbn(isbn):
        """Validate ISBN format and uniqueness."""
        if len(isbn) != 13 or not isbn.isdigit():
            raise ValidationError(_("ISBN must be a 13-digit number"))
        
        if Book.objects.filter(isbn=isbn).exists():
            raise ValidationError(_("Book with this ISBN already exists"))
    
    @staticmethod
    @log_method_call()
    def create_book(data):
        """Create a new book with validation."""
        isbn = data.get('isbn')
        if isbn:
            BookService.validate_isbn(isbn)
            
        total_copies = data.get('total_copies', 1)
        available_copies = data.get('available_copies', total_copies)
        
        if available_copies > total_copies:
            data['available_copies'] = total_copies
        
        book = Book.objects.create(**data)
        return book
    
    @staticmethod
    @log_method_call()
    def update_book(book, data):
        """Update an existing book."""
        if 'isbn' in data and data['isbn'] != book.isbn:
            BookService.validate_isbn(data['isbn'])
        
        for key, value in data.items():
            setattr(book, key, value)
        
        if book.available_copies > book.total_copies:
            book.available_copies = book.total_copies
            
        book.save()
        return book
