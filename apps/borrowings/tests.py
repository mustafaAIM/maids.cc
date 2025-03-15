from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.books.models import Book
from apps.patrons.models import Patron
from .models import BorrowingRecord

User = get_user_model()

class BorrowingAPITestCase(APITestCase):
    """Test cases for borrowing endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.librarian = User.objects.create_user(
            email='librarian@example.com',
            password='password123',
            role='librarian'
        )
        
        self.patron_user = User.objects.create_user(
            email='patron@example.com',
            password='password123',
            role='patron'
        )
        
        self.book1 = Book.objects.create(
            title="Available Book",
            author="Test Author",
            isbn="1234567890123",
            publication_year=2020,
            available_copies=3,
            total_copies=3
        )
        
        self.book2 = Book.objects.create(
            title="Unavailable Book",
            author="Test Author",
            isbn="9876543210987",
            publication_year=2021,
            available_copies=0,
            total_copies=1
        )
        
        self.patron1 = Patron.objects.create(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone_number="1234567890",
            member_id="P12345",
            active=True
        )
        
        self.patron2 = Patron.objects.create(
            first_name="Jane",
            last_name="Smith",
            email="jane.smith@example.com",
            phone_number="9876543210",
            member_id="P67890",
            active=False  
        )
        
        self.borrowing = BorrowingRecord.objects.create(
            book=self.book1,
            patron=self.patron1,
            borrow_date=timezone.now(),
            due_date=timezone.now() + timezone.timedelta(days=14),
            status="borrowed"
        )
        
        self.book1.available_copies = 2
        self.book1.save()
        
        self.borrow_url = reverse('borrowings:borrowing-borrow-book', kwargs={
            'book_id': self.book1.pk,
            'patron_id': self.patron1.pk
        })
        
        self.return_url = reverse('borrowings:borrowing-return-book', kwargs={
            'book_id': self.book1.pk,
            'patron_id': self.patron1.pk
        })
        
        self.borrow_unavailable_url = reverse('borrowings:borrowing-borrow-book', kwargs={
            'book_id': self.book2.pk,
            'patron_id': self.patron1.pk
        })
        
        self.borrow_inactive_patron_url = reverse('borrowings:borrowing-borrow-book', kwargs={
            'book_id': self.book1.pk,
            'patron_id': self.patron2.pk
        })
    
    def test_borrow_book_as_librarian(self):
        """Test borrowing a book as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        
        new_patron = Patron.objects.create(
            first_name="New",
            last_name="Patron",
            email="new.patron@example.com",
            phone_number="5551234567",
            member_id="P54321",
            active=True
        )
        
        borrow_url = reverse('borrowings:borrowing-borrow-book', kwargs={
            'book_id': self.book1.pk,
            'patron_id': new_patron.pk
        })
        
        data = {'notes': 'Test borrowing'}
        response = self.client.post(borrow_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Book borrowed successfully')
        self.assertEqual(response.data['data']['book'], self.book1.pk)
        self.assertEqual(response.data['data']['patron'], new_patron.pk)
        self.assertEqual(response.data['data']['status'], 'borrowed')
        
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.available_copies, 1)
    
    def test_borrow_book_as_patron(self):
        """Test borrowing a book as a patron (should be forbidden)"""
        self.client.force_authenticate(user=self.patron_user)
        
        data = {'notes': 'Test borrowing'}
        response = self.client.post(self.borrow_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_borrow_book_unauthenticated(self):
        """Test borrowing a book without authentication"""
        data = {'notes': 'Test borrowing'}
        response = self.client.post(self.borrow_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    # def test_borrow_unavailable_book(self):
    #     """Test borrowing a book that has no available copies"""
    #     self.client.force_authenticate(user=self.librarian)
        
    #     data = {'notes': 'Test borrowing unavailable book'}
    #     response = self.client.post(self.borrow_unavailable_url, data, format='json')
        
    #     self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    #     self.assertFalse(response.data['success'])
    #     self.assertIn('This book is not available for borrowing', str(response.data))
    
    def test_borrow_by_inactive_patron(self):
        """Test borrowing a book for an inactive patron"""
        self.client.force_authenticate(user=self.librarian)
        
        data = {'notes': 'Test borrowing for inactive patron'}
        response = self.client.post(self.borrow_inactive_patron_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('This patron is not active', str(response.data))
    
    def test_double_borrow_same_book(self):
        """Test borrowing a book that is already borrowed by the same patron"""
        self.client.force_authenticate(user=self.librarian)
        
        data = {'notes': 'Test double borrowing'}
        response = self.client.post(self.borrow_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('already has this book borrowed', str(response.data))
    
    def test_return_book_as_librarian(self):
        """Test returning a borrowed book as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        
        data = {'notes': 'Test return'}
        response = self.client.put(self.return_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Book returned successfully')
        self.assertEqual(response.data['data']['status'], 'returned')
        self.assertIsNotNone(response.data['data']['return_date'])
        
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.available_copies, 3)
    
    def test_return_book_as_patron(self):
        """Test returning a book as a patron (should be forbidden)"""
        self.client.force_authenticate(user=self.patron_user)
        
        data = {'notes': 'Test return'}
        response = self.client.put(self.return_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_return_nonexistent_borrowing(self):
        """Test returning a book that isn't borrowed"""
        self.client.force_authenticate(user=self.librarian)
        
        data = {'notes': 'Return for test'}
        self.client.put(self.return_url, data, format='json')
        
        response = self.client.put(self.return_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('No active borrowing record found', str(response.data))
    
    def test_list_borrowings(self):
        """Test listing all borrowing records"""
        self.client.force_authenticate(user=self.librarian)
        
        list_url = reverse('borrowings:borrowing-list')
        response = self.client.get(list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)