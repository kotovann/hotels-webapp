from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class LogoutTest(APITestCase):
    def setUp(self):
        self.logout_url = reverse('logout')
        self.user = User.objects.create_user(
            last_name='Test',
            first_name='User',
            email='test@example.com',
            phone_number='+79999999999',
            password='GoodPassword432+',
        )
        self.client.force_authenticate(user=self.user)

    def test_logout_success(self):
        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)
        response = self.client.post(self.logout_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        token_jti = refresh.payload.get('jti')
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=token_jti).exists())

    def test_logout_without_refresh(self):
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
