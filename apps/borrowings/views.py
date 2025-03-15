from django.shortcuts import render
from django.utils.translation import gettext_lazy as _
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from apps.core.mixins.response_mixins import ResponseMixin
from apps.core.aspects.decorators import log_method_call, measure_performance, log_transaction
from apps.authentication.permissions import IsLibrarian

from .models import BorrowingRecord
from .serializers import BorrowingRecordSerializer, BorrowBookSerializer, ReturnBookSerializer
from .services import BorrowingService


class BorrowingViewSet(ResponseMixin, viewsets.ModelViewSet):
    """
    ViewSet for borrowing operations.
    """
    queryset = BorrowingRecord.objects.all()
    serializer_class = BorrowingRecordSerializer
    permission_classes = [IsAuthenticated, IsLibrarian]
    
    @transaction.atomic
    @log_transaction("BOOK_BORROW")
    @log_method_call("Borrow Book")
    @measure_performance("Borrow Book Performance")
    @action(detail=False, methods=['post'], url_path='borrow/(?P<book_id>[^/.]+)/patron/(?P<patron_id>[^/.]+)')
    def borrow_book(self, request, book_id, patron_id):
        """Allow a patron to borrow a book"""
        
        serializer = BorrowBookSerializer(
            data=request.data,
            context={'book_id': book_id, 'patron_id': patron_id}
        )
        serializer.is_valid(raise_exception=True)
        
        book = serializer.validated_data['book']
        patron = serializer.validated_data['patron']
        notes = serializer.validated_data.get('notes', '')
        
        borrowing_record = BorrowingService.borrow_book(book, patron, notes)
        
        result_serializer = BorrowingRecordSerializer(borrowing_record)
        return self.send_success_response(
            data=result_serializer.data,
            message=_("Book borrowed successfully"),
            status=status.HTTP_201_CREATED
        )
    
    @transaction.atomic
    @log_transaction("BOOK_RETURN")
    @log_method_call("Return Book")
    @measure_performance("Return Book Performance")
    @action(detail=False, methods=['put'], url_path='return/(?P<book_id>[^/.]+)/patron/(?P<patron_id>[^/.]+)')
    def return_book(self, request, book_id, patron_id):
        """Record the return of a borrowed book by a patron"""
        
        serializer = ReturnBookSerializer(
            data=request.data,
            context={'book_id': book_id, 'patron_id': patron_id}
        )
        serializer.is_valid(raise_exception=True)
        
        borrowing_record = serializer.validated_data['borrowing_record']
        notes = serializer.validated_data.get('notes', '')
        
        updated_record = BorrowingService.return_book(borrowing_record, notes)
        
        result_serializer = BorrowingRecordSerializer(updated_record)
        return self.send_success_response(
            data=result_serializer.data,
            message=_("Book returned successfully"),
            status=status.HTTP_200_OK
        )
