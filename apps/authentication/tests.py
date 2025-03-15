from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()

class AuthenticationViewTest(APITestCase):
    """Test cases for the authentication login endpoint"""
    
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
        
        self.login_url = reverse('authentication:login')
        
        self.valid_credentials = {
            'email': 'librarian@example.com',
            'password': 'password123'
        }
        
        self.invalid_credentials = {
            'email': 'librarian@example.com',
            'password': 'wrongpassword'
        }
        
        self.nonexistent_credentials = {
            'email': 'nonexistent@example.com',
            'password': 'password123'
        }

    def test_login_success(self):
        """Test successful login"""
        response = self.client.post(self.login_url, self.valid_credentials, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Login successful')
        self.assertIn('data', response.data)
        self.assertIn('refresh', response.data['data'])
        self.assertIn('access', response.data['data'])
        self.assertIn('user_id', response.data['data'])
        self.assertIn('email', response.data['data'])
        self.assertEqual(response.data['data']['email'], 'librarian@example.com')
    
    def test_login_failure(self):
        """Test login with invalid credentials"""
        response = self.client.post(self.login_url, self.invalid_credentials, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Invalid credentials')
    
    def test_login_nonexistent_user(self):
        """Test login with non-existent user"""
        response = self.client.post(self.login_url, self.nonexistent_credentials, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        self.assertEqual(response.data['message'], 'Invalid credentials')
    
    def test_login_missing_fields(self):
        """Test login with missing fields"""
        response = self.client.post(self.login_url, {'email': 'librarian@example.com'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(self.login_url, {'password': 'password123'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        response = self.client.post(self.login_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_account_locking(self):
        """Test account locking after multiple failed login attempts"""
        for _ in range(5):
            response = self.client.post(self.login_url, self.invalid_credentials, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        user = User.objects.get(email='librarian@example.com')
        self.assertTrue(user.is_locked)
        
        response = self.client.post(self.login_url, self.valid_credentials, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(response.data['success'])
        self.assertIn('Account is locked', response.data['message'])
        
        user.locked_until = None
        user.login_attempts = 0
        user.save()

    def test_login_method_not_allowed(self):
        """Test that only POST is allowed for login"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class UserRegistrationViewTest(APITestCase):
    """Test cases for the user registration endpoint"""
    
    def setUp(self):
        """Set up test data"""
        self.register_url = reverse('authentication:register')
        
        self.valid_patron_data = {
            'email': 'newpatron@example.com',
            'first_name': 'New',
            'last_name': 'Patron',
            'role': 'patron',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        
        self.valid_librarian_data = {
            'email': 'newlibrarian@example.com',
            'first_name': 'New',
            'last_name': 'Librarian',
            'role': 'librarian',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        
        self.invalid_data_mismatched_passwords = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'patron',
            'password': 'Password123!',
            'confirm_password': 'DifferentPassword123!'
        }
        
        self.invalid_data_weak_password = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'patron',
            'password': '12345',
            'confirm_password': '12345'
        }
        
        self.invalid_data_invalid_email = {
            'email': 'not-an-email',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'patron',
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }
        
        self.invalid_data_invalid_role = {
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'role': 'admin',  # Invalid role
            'password': 'Password123!',
            'confirm_password': 'Password123!'
        }

    def test_register_patron_success(self):
        """Test successful patron registration"""
        response = self.client.post(self.register_url, self.valid_patron_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'User registered successfully')
        self.assertEqual(response.data['data']['email'], 'newpatron@example.com')
        self.assertEqual(response.data['data']['role'], 'patron')
        self.assertFalse(response.data['data']['is_librarian'])
        
        self.assertTrue(User.objects.filter(email='newpatron@example.com').exists())
    
    def test_register_librarian_success(self):
        """Test successful librarian registration"""
        response = self.client.post(self.register_url, self.valid_librarian_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['data']['email'], 'newlibrarian@example.com')
        self.assertEqual(response.data['data']['role'], 'librarian')
        self.assertTrue(response.data['data']['is_librarian'])
        
        self.assertTrue(User.objects.filter(email='newlibrarian@example.com').exists())
    
    def test_register_mismatched_passwords(self):
        """Test registration with mismatched passwords"""
        response = self.client.post(self.register_url, self.invalid_data_mismatched_passwords, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
        self.assertIn('confirm_password', response.data['errors'])
    
    def test_register_invalid_email(self):
        """Test registration with invalid email"""
        response = self.client.post(self.register_url, self.invalid_data_invalid_email, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
        self.assertIn('email', response.data['errors'])
    
    def test_register_invalid_role(self):
        """Test registration with invalid role"""
        response = self.client.post(self.register_url, self.invalid_data_invalid_role, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
        self.assertIn('role', response.data['errors'])
    
    def test_register_duplicate_email(self):
        """Test registration with an email that already exists"""
        response = self.client.post(self.register_url, self.valid_patron_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        response = self.client.post(self.register_url, self.valid_patron_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('errors', response.data)
        self.assertIn('email', response.data['errors'])


class UserManagementViewSetTest(APITestCase):
    """Test cases for the user management viewset (librarian only access)"""
    
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
        
        self.another_patron = User.objects.create_user(
            email='another@example.com',
            password='password123',
            role='patron'
        )
        
        self.users_list_url = reverse('authentication:user-management-list')
        self.user_detail_url = reverse('authentication:user-management-detail', kwargs={'pk': self.patron.pk})
        
        self.valid_update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }

    def test_list_users_as_librarian(self):
        """Test listing all users as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.get(self.users_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'Users retrieved successfully')
        self.assertEqual(len(response.data['data']), 3)  
    
    def test_list_users_as_patron(self):
        """Test listing users as a patron (should be forbidden)"""
        self.client.force_authenticate(user=self.patron)
        response = self.client.get(self.users_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_list_users_unauthenticated(self):
        """Test listing users without authentication"""
        response = self.client.get(self.users_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_retrieve_user_as_librarian(self):
        """Test retrieving user details as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.get(self.user_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], 'User details retrieved successfully')
        self.assertEqual(response.data['data']['email'], 'patron@example.com')
    
    def test_update_user_as_librarian(self):
        """Test updating user as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.patch(self.user_detail_url, self.valid_update_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.patron.refresh_from_db()
        self.assertEqual(self.patron.first_name, 'Updated')
        self.assertEqual(self.patron.last_name, 'Name')
    
    def test_delete_user_as_librarian(self):
        """Test deleting user as a librarian"""
        self.client.force_authenticate(user=self.librarian)
        response = self.client.delete(self.user_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        self.patron.refresh_from_db()
        self.assertTrue(self.patron.is_deleted)
        self.assertIsNotNone(self.patron.deleted_at)
