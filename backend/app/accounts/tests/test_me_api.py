from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class MeViewSetTest(APITestCase):
    def setUp(self):
        self.base_url = reverse('me')
        self.deactivate_url = reverse('me-deactivate')
        self.admin = User.objects.create_user(
            email='admin@example.com',
            first_name='Admin',
            last_name='Admin',
            phone_number='+79000000000',
            password='GoodPassword432+'
        )
        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            first_name='Moderator',
            last_name='Test',
            phone_number='+79222222222',
            password='GoodPassword432+'
        )
        self.guest = User.objects.create_user(
            email='guest@example.com',
            first_name='Guest',
            last_name='Test',
            phone_number='+79333333333',
            password='GoodPassword432+'
        )
        self.no_role_user = User.objects.create_user(
            email='user@example.com',
            first_name='User',
            last_name='NoRole',
            phone_number='+79444444444',
            password='GoodPassword432+'
        )

        self.admin.assign_role(role=User.Role.ADMIN)
        self.moderator.assign_role(role=User.Role.MODERATOR)
        self.guest.assign_role(role=User.Role.GUEST)

    def test_unauthenticated_cannot_retrieve_me(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_update_me(self):
        response = self.client.patch(self.base_url, {'first_name': 'NewName'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unauthenticated_cannot_deactivate_me(self):
        url = reverse('me-deactivate')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_any_authenticated_user_can_retrieve_self(self):
        users = [self.admin, self.moderator, self.guest, self.no_role_user]
        for user in users:
            with self.subTest(user=user.email):
                self.client.force_authenticate(user)
                response = self.client.get(self.base_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['email'], user.email)
                self.assertEqual(response.data['first_name'], user.first_name)
                self.assertEqual(response.data['last_name'], user.last_name)
                self.assertEqual(response.data['phone_number'], user.phone_number)
                expected_role = user.role
                self.assertEqual(response.data['role'], expected_role)

    def test_guest_can_deactivate_own_account(self):
        self.client.force_authenticate(self.guest)
        url = reverse('me-deactivate')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.guest.refresh_from_db()
        self.assertFalse(self.guest.is_active)

    def test_non_guest_cannot_deactivate_own_account(self):
        non_guests = [self.admin, self.moderator, self.no_role_user]
        for user in non_guests:
            with self.subTest(user=user.email):
                self.client.force_authenticate(user)
                response = self.client.post(self.deactivate_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                user.refresh_from_db()
                self.assertTrue(user.is_active)
