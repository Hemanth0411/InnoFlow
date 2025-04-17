# users/tests.py
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
import json
from .models import UserProfile

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            bio='Test bio',
            company='Test Company'
        )

    def test_user_creation(self):
        """Test user creation with custom fields"""
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.bio, 'Test bio')
        self.assertEqual(self.user.company, 'Test Company')
        self.assertTrue(self.user.check_password('testpassword123'))

    def test_user_str_method(self):
        """Test the string representation of user objects"""
        self.assertEqual(str(self.user), 'testuser')


class UserAPITest(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            bio='Test bio'
        )
        
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpassword123'
        )
        
        # URLs
        self.register_url = reverse('register')
        self.me_url = reverse('user-me')
        self.users_url = reverse('userprofile-list')
        
    def get_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
        
    def authenticate(self, user):
        tokens = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')

    def test_register_user(self):
        """Test user registration endpoint"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'newpassword123',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 3)
        
        new_user = User.objects.get(username='newuser')
        self.assertEqual(new_user.email, 'newuser@example.com')
        self.assertEqual(new_user.first_name, 'New')

    def test_register_with_mismatched_passwords(self):
        """Test registration with mismatched passwords fails"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'newpassword123',
            'password2': 'differentpassword',
            'first_name': 'New',
            'last_name': 'User'
        }
        
        response = self.client.post(self.register_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_me_endpoint(self):
        """Test that users can get their own profile information"""
        self.authenticate(self.user)
        
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['email'], 'test@example.com')
        self.assertEqual(response.data['bio'], 'Test bio')

    def test_update_user_profile(self):
        """Test that users can update their profile"""
        self.authenticate(self.user)
        
        user_detail_url = reverse('userprofile-detail', kwargs={'pk': self.user.id})
        
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Updated bio',
            'company': 'New Company'
        }
        
        response = self.client.patch(user_detail_url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Refresh user from database
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.bio, 'Updated bio')
        self.assertEqual(self.user.company, 'New Company')

    def test_user_list_permission(self):
        """Test that regular users can't access user list but admins can"""
        # Try as regular user
        self.authenticate(self.user)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Regular users should only see their own user record
        self.assertEqual(len(response.data), 1)
        
        # Try as admin
        self.authenticate(self.admin_user)
        response = self.client.get(self.users_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Admin should see all user records
        self.assertEqual(len(response.data), 2)

    def test_unauthorized_access(self):
        """Test that unauthenticated requests are denied"""
        # No authentication
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserFormsTest(TestCase):
    def test_user_creation_form(self):
        """Test the custom user creation form"""
        from .forms import UserProfileCreationForm
        
        form_data = {
            'username': 'formuser',
            'email': 'form@example.com',
            'first_name': 'Form',
            'last_name': 'User',
            'password1': 'formpassword123',
            'password2': 'formpassword123',
        }
        
        form = UserProfileCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Save the form
        user = form.save()
        self.assertEqual(user.username, 'formuser')
        self.assertEqual(user.email, 'form@example.com')
        self.assertEqual(user.first_name, 'Form')

    def test_user_change_form(self):
        """Test the custom user change form"""
        from .forms import UserProfileChangeForm
        
        # Create a user first
        user = User.objects.create_user(
            username='changeuser',
            email='change@example.com',
            password='changepassword123'
        )
        
        form_data = {
            'username': 'changeuser',
            'email': 'updated@example.com',
            'first_name': 'Changed',
            'last_name': 'User',
            'bio': 'Updated bio',
            'company': 'Updated Company',
        }
        
        form = UserProfileChangeForm(data=form_data, instance=user)
        self.assertTrue(form.is_valid())
        
        # Save the form
        updated_user = form.save()
        self.assertEqual(updated_user.email, 'updated@example.com')
        self.assertEqual(updated_user.first_name, 'Changed')
        self.assertEqual(updated_user.bio, 'Updated bio')