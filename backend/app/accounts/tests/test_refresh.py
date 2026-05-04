from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class RefreshTest(APITestCase):
    def setUp(self):
        self.refresh_url = reverse('token-refresh')
        self.user = User.objects.create_user(
            last_name='Test',
            first_name='User',
            email='test@example.com',
            phone_number='+79999999999',
            password='GoodPassword432+',
        )

    def test_refresh_success(self):
        self.client.force_authenticate(user=self.user)
        refresh = RefreshToken.for_user(self.user)
        refresh_token = str(refresh)
        response = self.client.post(self.refresh_url, {'refresh': refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        old_token_jti = refresh.payload.get('jti')
        new_token_jti = RefreshToken(response.data['refresh']).payload.get('jti')
        self.assertTrue(BlacklistedToken.objects.filter(token__jti=old_token_jti).exists())
        self.assertFalse(BlacklistedToken.objects.filter(token__jti=new_token_jti).exists())
