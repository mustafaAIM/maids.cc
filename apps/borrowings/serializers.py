from rest_framework import serializers
from .models import BorrowingRecord
from apps.books.models import Book
from apps.patrons.models import Patron

class BorrowingRecordSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(source='book.title', read_only=True)
    patron_name = serializers.CharField(source='patron.full_name', read_only=True)
    is_overdue = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = BorrowingRecord
        fields = [
            'id', 'book', 'book_title', 'patron', 'patron_name', 
            'borrow_date', 'due_date', 'return_date', 'status',
            'notes', 'is_overdue', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class BorrowBookSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        book_id = self.context.get('book_id')
        patron_id = self.context.get('patron_id')
        
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError({"book_id": "Book does not exist."})
        
        try:
            patron = Patron.objects.get(pk=patron_id)
        except Patron.DoesNotExist:
            raise serializers.ValidationError({"patron_id": "Patron does not exist."})
        
        if book.available_copies <= 0:
            raise serializers.ValidationError({"book_id": "This book is not available for borrowing."})
        
        if not patron.active:
            raise serializers.ValidationError({"patron_id": "This patron is not active."})
        
        if BorrowingRecord.objects.filter(
            book=book, 
            patron=patron, 
            status__in=[BorrowingRecord.BORROWED, BorrowingRecord.PENDING]
        ).exists():
            raise serializers.ValidationError(
                {"non_field_errors": "This patron already has this book borrowed."}
            )
        
        attrs['book'] = book
        attrs['patron'] = patron
        
        return attrs

class ReturnBookSerializer(serializers.Serializer):
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        book_id = self.context.get('book_id')
        patron_id = self.context.get('patron_id')
        
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            raise serializers.ValidationError({"book_id": "Book does not exist."})
        
        try:
            patron = Patron.objects.get(pk=patron_id)
        except Patron.DoesNotExist:
            raise serializers.ValidationError({"patron_id": "Patron does not exist."})
        
        try:
            borrowing_record = BorrowingRecord.objects.get(
                book=book,
                patron=patron,
                status__in=[BorrowingRecord.BORROWED, BorrowingRecord.OVERDUE]
            )
        except BorrowingRecord.DoesNotExist:
            raise serializers.ValidationError(
                {"non_field_errors": "No active borrowing record found for this book and patron."}
            )
        
        attrs['book'] = book
        attrs['patron'] = patron
        attrs['borrowing_record'] = borrowing_record
        
        return attrs
