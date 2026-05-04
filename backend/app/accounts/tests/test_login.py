from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class LoginTest(APITestCase):
    def setUp(self):
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            last_name='Test',
            first_name='User',
            email='test@example.com',
            phone_number='+79999999999',
            password='GoodPassword432+',
        )
        self.login_data = {
            'email': 'test@example.com',
            'password': 'GoodPassword432+',
        }

    def test_login_success(self):
        response = self.client.post(self.login_url, self.login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_nonexist_email(self):
        response = self.client.post(self.login_url, {
            'email': 'wrong@example.com',
            'password': 'GoodPassword432+'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_wrong_password(self):
        response = self.client.post(self.login_url, {**self.login_data, 'password': 'wrong'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
