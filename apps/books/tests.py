from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from apps.books.models import Book

User = get_user_model()

class BookAPITestCase(APITestCase):
    """Test case for the Book API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.librarian = User.objects.create_user(
            email='librarian@example.com',
            password='password123',
            role='librarian'
        )
        
        self.patron = User.objects.create_user(
            email='patron@example.com',
            password='password123',
            role='patron'
        )
        
        self.book1 = Book.objects.create(
            title='Test Book 1',
            author='Test Author 1',
            isbn='1234567890123',
            publication_year=2020,
            available_copies=5,
            total_copies=5
        )
        
        self.book2 = Book.objects.create(
            title='Test Book 2',
            author='Test Author 2',
            isbn='9876543210987',
            publication_year=2021,
            available_copies=3,
            total_copies=3
        )
        
        self.list_url = reverse('book-list')
        self.detail_url = reverse('book-detail', kwargs={'pk': self.book1.pk})
        
        self.valid_book_data = {
            'title': 'New Test Book',
            'author': 'New Test Author',
            'isbn': '5555555555555',
            'publication_year': 2022,
            'available_copies': 10,
            'total_copies': 10
        }
        
        self.invalid_book_data = {
            'title': '',
            'author': 'Some Author',
            'isbn': '123'
        }

    def test_get_all_books_unauthenticated(self):
        """Test retrieving all books without authentication - should require auth"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_get_all_books_authenticated(self):
        """Test retrieving all books as an authenticated user"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
    
    def test_get_single_book(self):
        """Test retrieving a single book by ID - should require auth"""
        # Authenticate first since the endpoint requires it
        self.client.force_authenticate(user=self.patron)
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['title'], 'Test Book 1')
    
    def test_get_nonexistent_book(self):
        """Test retrieving a book that doesn't exist - should require auth"""
        # Authenticate first since the endpoint requires it
        self.client.force_authenticate(user=self.patron)
        non_existent_url = reverse('book-detail', kwargs={'pk': 999})
        response = self.client.get(non_existent_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_create_book_as_librarian(self):
        """Test creating a new book as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.post(self.list_url, self.valid_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 3)
        self.assertEqual(Book.objects.latest('id').title, 'New Test Book')
    
    def test_create_book_as_patron(self):
        """Test creating a book as a patron (should be restricted)"""
        self.client.force_authenticate(user=self.patron)
        response = self.client.post(self.list_url, self.valid_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 2)
    
    def test_create_book_unauthenticated(self):
        """Test creating a book without authentication"""
        response = self.client.post(self.list_url, self.valid_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 2)
    
    def test_create_book_invalid_data(self):
        """Test creating a book with invalid data"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.post(self.list_url, self.invalid_book_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Book.objects.count(), 2) 
    
    def test_update_book_as_librarian(self):
        """Test updating a book as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        update_data = {
            'title': 'Updated Book Title',
            'author': 'Test Author 1',
            'isbn': '1234567890123'       
        }
        response = self.client.patch(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Updated Book Title')
    
    def test_update_book_as_patron(self):
        """Test updating a book as a patron (should be restricted)"""
        self.client.force_authenticate(user=self.patron)
        update_data = {'title': 'Patron Updated Title'}
        response = self.client.patch(self.detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.book1.refresh_from_db()
        self.assertEqual(self.book1.title, 'Test Book 1')
    
    def test_delete_book_as_librarian(self):
        """Test deleting a book as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Book.objects.count(), 1)
    
    def test_delete_book_as_patron(self):
        """Test deleting a book as a patron (should be restricted)"""
        self.client.force_authenticate(user=self.patron)
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Book.objects.count(), 2)  

    