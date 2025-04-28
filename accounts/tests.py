from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from accounts.forms import SignUpForm


class SignupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.signup_url = reverse('signup')
        self.home_url = reverse('home')
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpassword123',
            'password2': 'testpassword123',
        }

    def test_signup_page_GET(self):
        response = self.client.get(self.signup_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_signup_page_POST_valid_data(self):
        response = self.client.post(self.signup_url, self.user_data)

        self.assertTrue(User.objects.filter(username=self.user_data['username']).exists())

        self.assertRedirects(response, self.home_url)

        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(user.is_authenticated)

    def test_signup_page_POST_invalid_data(self):
        invalid_data = self.user_data.copy()
        invalid_data['password2'] = 'differentpassword'

        response = self.client.post(self.signup_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

        self.assertFalse(User.objects.filter(username=self.user_data['username']).exists())

        self.assertTrue(response.context['form'].errors)

    def test_signup_page_POST_existing_username(self):
        User.objects.create_user(
            username=self.user_data['username'],
            email='existing@example.com',
            password='existingpassword123'
        )

        response = self.client.post(self.signup_url, self.user_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

        self.assertIn('username', response.context['form'].errors)

    def test_signup_bad_email(self):
        invalid_data = self.user_data.copy()
        invalid_data['email'] = 'invalid-email'

        response = self.client.post(self.signup_url, invalid_data)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')

        self.assertFalse(User.objects.filter(username=self.user_data['username']).exists())

        self.assertTrue(response.context['form'].errors)