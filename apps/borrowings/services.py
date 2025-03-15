from django.utils import timezone
from django.db import transaction
from .models import BorrowingRecord
from django.core.exceptions import ValidationError

class BorrowingService:
    """Service class for borrowing operations"""
    
    @staticmethod
    @transaction.atomic
    def borrow_book(book, patron, notes=""):
        """
        Create a borrowing record to lend a book to a patron
        
        Args:
            book: The Book object to borrow
            patron: The Patron who is borrowing the book
            notes: Optional notes about the borrowing
            
        Returns:
            The created BorrowingRecord
        """
        if book.available_copies <= 0:
            raise ValidationError("This book is not available for borrowing.")
        
        borrowing_record = BorrowingRecord(
            book=book,
            patron=patron,
            status=BorrowingRecord.BORROWED,
            borrow_date=timezone.now(),
            due_date=timezone.now() + timezone.timedelta(days=14),
            notes=notes
        )
        
        book.available_copies = max(0, book.available_copies - 1)
        book.save(update_fields=['available_copies'])
        
        borrowing_record.save()
        
        return borrowing_record
    
    @staticmethod
    @transaction.atomic
    def return_book(borrowing_record, notes=""):
        """
        Record the return of a borrowed book
        
        Args:
            borrowing_record: The BorrowingRecord to update
            notes: Optional notes about the return
            
        Returns:
            The updated BorrowingRecord
        """
        borrowing_record.status = BorrowingRecord.RETURNED
        borrowing_record.return_date = timezone.now()
        
        if notes:
            borrowing_record.notes += f"\nReturn notes: {notes}"
        
        book = borrowing_record.book
        book.available_copies = min(book.total_copies, book.available_copies + 1)
        book.save(update_fields=['available_copies'])
        
        borrowing_record.save()
        
        return borrowing_record
    
    @staticmethod
    def check_overdue_books():
        """
        Update status of overdue books
        
        Returns:
            Number of records updated
        """
        now = timezone.now()
        
        overdue_records = BorrowingRecord.objects.filter(
            status=BorrowingRecord.BORROWED,
            due_date__lt=now
        )
        
        count = overdue_records.count()
        overdue_records.update(status=BorrowingRecord.OVERDUE)
        
        return count
