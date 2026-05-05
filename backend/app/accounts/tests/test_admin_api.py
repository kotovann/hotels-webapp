from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()


class AdminViewSetTest(APITestCase):
    def setUp(self):
        self.base_url = reverse('admin-list')

        self.admin1 = User.objects.create_user(
            email='admin1@example.com',
            first_name='Admin',
            last_name='One',
            phone_number='+79000000001',
            password='GoodPassword432+'
        )
        self.admin2 = User.objects.create_user(
            email='admin2@example.com',
            first_name='Admin',
            last_name='Two',
            phone_number='+79000000002',
            password='GoodPassword432+'
        )
        self.moderator = User.objects.create_user(
            email='moderator@example.com',
            first_name='Moderator',
            last_name='Test',
            phone_number='+79111111111',
            password='GoodPassword432+'
        )
        self.guest = User.objects.create_user(
            email='guest@example.com',
            first_name='Guest',
            last_name='Test',
            phone_number='+79222222222',
            password='GoodPassword432+'
        )

        self.admin1.assign_role(role=User.Role.ADMIN)
        self.admin2.assign_role(role=User.Role.ADMIN)
        self.moderator.assign_role(role=User.Role.MODERATOR)
        self.guest.assign_role(role=User.Role.GUEST)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_other_users_cannot_access(self):
        users = [self.guest, self.moderator]
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                response = self.client.get(self.base_url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_admins(self):
        self.client.force_authenticate(self.admin1)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        emails = [user['email'] for user in response.data]
        self.assertIn(self.admin1.email, emails)
        self.assertIn(self.admin2.email, emails)

    def test_search_by_last_name(self):
        self.client.force_authenticate(self.admin1)
        response = self.client.get(self.base_url, {'search': 'Two'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['last_name'], 'Two')

    def test_search_by_email(self):
        self.client.force_authenticate(self.admin1)
        response = self.client.get(self.base_url, {'search': 'admin1@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['email'], self.admin1.email)

    def test_search_by_phone_number(self):
        self.client.force_authenticate(self.admin1)
        response = self.client.get(self.base_url, {'search': '79000000001'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['phone_number'], self.admin1.phone_number)

    def test_ordering_by_email(self):
        self.client.force_authenticate(self.admin1)
        response = self.client.get(self.base_url, {'ordering': '-email'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [user['email'] for user in response.data]
        self.assertEqual(emails, sorted(emails, reverse=True))

    def test_filter_by_is_active(self):
        self.admin2.is_active = False
        self.admin2.save()
        self.client.force_authenticate(self.admin1)

        response_active = self.client.get(self.base_url, {'is_active': 'True'})
        self.assertEqual(len(response_active.data), 1)
        self.assertEqual(response_active.data[0]['email'], self.admin1.email)

        response_inactive = self.client.get(self.base_url, {'is_active': 'False'})
        self.assertEqual(len(response_inactive.data), 1)
        self.assertEqual(response_inactive.data[0]['email'], self.admin2.email)

    def test_admin_can_retrieve_admin(self):
        self.client.force_authenticate(self.admin1)
        url = reverse('admin-detail', kwargs={'pk': self.admin2.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.admin2.email)

    def test_other_users_cannot_retrieve_admin(self):
        users = [self.guest, self.moderator]
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                url = reverse('admin-detail', kwargs={'pk': self.admin2.pk})
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_retrieve_nonexistent_admin_returns_404(self):
        self.client.force_authenticate(self.admin1)
        url = reverse('admin-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_create_admin(self):
        self.client.force_authenticate(self.admin1)
        new_admin_data = {
            'email': 'newadmin@example.com',
            'first_name': 'Admin',
            'last_name': 'New',
            'phone_number': '+79777777777',
            'password': 'GoodPassword432+',
        }
        response = self.client.post(self.base_url, new_admin_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = User.objects.filter(email=new_admin_data['email']).first()
        self.assertIsNotNone(user)
        self.assertTrue(user.is_admin)
        self.assertEqual(user.role, User.Role.ADMIN)
        self.assertEqual(user.first_name, new_admin_data['first_name'])
        self.assertEqual(user.last_name, new_admin_data['last_name'])
        self.assertEqual(user.phone_number, new_admin_data['phone_number'])
        self.assertTrue(user.check_password(new_admin_data['password']))

    def test_other_users_cannot_create_admin(self):
        users = [self.guest, self.moderator]
        new_admin_data = {
            'email': 'newadmin@example.com',
            'first_name': 'Admin',
            'last_name': 'New',
            'phone_number': '+79777777777',
            'password': 'GoodPassword432+',
        }
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                response = self.client.post(self.base_url, new_admin_data)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_admin_with_invalid_data_returns_400(self):
        wrong_email = {
            'email': 'not-an-email',
            'first_name': 'Admin',
            'last_name': 'New1',
            'phone_number': '+79999999999',
            'password': 'GoodPassword432+',
        }
        wrong_phone = {
            'email': 'new2@example.com',
            'first_name': 'Admin',
            'last_name': 'New2',
            'phone_number': '12345',
            'password': 'GoodPassword432+',
        }
        no_email = {
            'first_name': 'Admin',
            'last_name': 'New3',
            'phone_number': '+79888888888',
            'password': 'GoodPassword432+',
        }
        no_phone = {
            'email': 'new4@example.com',
            'first_name': 'Admin',
            'last_name': 'New4',
            'password': 'GoodPassword432+',
        }
        no_last_name = {
            'email': 'new5@example.com',
            'first_name': 'Admin',
            'phone_number': '+79555555555',
            'password': 'GoodPassword432+',
        }
        self.client.force_authenticate(self.admin1)

        response1 = self.client.post(self.base_url, wrong_email)
        self.assertEqual(response1.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=wrong_email['phone_number']).exists())

        response2 = self.client.post(self.base_url, wrong_phone)
        self.assertEqual(response2.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=wrong_phone['email']).exists())

        response3 = self.client.post(self.base_url, no_email)
        self.assertEqual(response3.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=no_email['phone_number']).exists())

        response4 = self.client.post(self.base_url, no_phone)
        self.assertEqual(response4.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=no_phone['email']).exists())

        response5 = self.client.post(self.base_url, no_last_name)
        self.assertEqual(response5.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(User.objects.filter(email=no_last_name['email']).exists())

    def test_admin_can_update_admin(self):
        self.client.force_authenticate(self.admin1)
        url = reverse('admin-detail', kwargs={'pk': self.admin2.pk})
        response = self.client.patch(url, {'first_name': 'UpdatedName'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.admin2.refresh_from_db()
        self.assertEqual(self.admin2.first_name, 'UpdatedName')

    def test_other_users_cannot_update_admin(self):
        users = [self.guest, self.moderator]
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                url = reverse('admin-detail', kwargs={'pk': self.admin2.pk})
                response = self.client.patch(url, {'first_name': 'UpdatedName'})
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.admin2.refresh_from_db()
                self.assertEqual(self.admin2.first_name, 'Admin')

    def test_admin_can_delete_admin(self):
        self.client.force_authenticate(self.admin1)
        url = reverse('admin-detail', kwargs={'pk': self.admin2.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.admin2.pk).exists())

    def test_other_users_cannot_delete_admin(self):
        users = [self.guest, self.moderator]
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                url = reverse('admin-detail', kwargs={'pk': self.admin2.pk})
                response = self.client.delete(url)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertTrue(User.objects.filter(pk=self.admin2.pk).exists())
