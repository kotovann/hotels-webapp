from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status


User = get_user_model()


class GuestViewSetTest(APITestCase):
    def setUp(self):
        self.base_url = reverse('guest-list')
        self.admin = User.objects.create_user(
            email='admin@example.com',
            first_name='Admin',
            last_name='Test',
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
        self.guest1 = User.objects.create_user(
            email='guest1@example.com',
            first_name='Guest',
            last_name='One',
            phone_number='+79333333333',
            password='GoodPassword432+'
        )
        self.guest2 = User.objects.create_user(
            email='guest2@example.com',
            first_name='Guest',
            last_name='Two',
            phone_number='+79444444444',
            password='GoodPassword432+'
        )

        self.admin.assign_role(role=User.Role.ADMIN)
        self.moderator.assign_role(role=User.Role.MODERATOR)
        self.guest1.assign_role(role=User.Role.GUEST)
        self.guest2.assign_role(role=User.Role.GUEST)

    def test_unauthenticated_cannot_access(self):
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_guest_cannot_access(self):
        self.client.force_authenticate(self.guest1)
        response = self.client.get(self.base_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_staff_can_list_guests(self):
        users = [self.admin, self.moderator]
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                response = self.client.get(self.base_url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(len(response.data), 2)

    def test_search_by_last_name(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.base_url, {'search': 'One'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['last_name'], 'One')

    def test_ordering_by_email(self):
        self.client.force_authenticate(self.admin)
        response = self.client.get(self.base_url, {'ordering': '-email'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        emails = [g['email'] for g in response.data]
        self.assertEqual(emails, sorted(emails, reverse=True))

    def test_filter_guests_by_is_active(self):
        self.guest1.is_active = False
        self.guest1.save()
        self.client.force_authenticate(self.admin)

        response1 = self.client.get(self.base_url, {'is_active': 'True'})
        self.assertEqual(len(response1.data), 1)
        self.assertEqual(response1.data[0]['email'], self.guest2.email)

        response2 = self.client.get(self.base_url, {'is_active': 'False'})
        self.assertEqual(len(response2.data), 1)
        self.assertEqual(response2.data[0]['email'], self.guest1.email)

    def test_staff_can_retrieve_guest(self):
        users = [self.admin, self.moderator]
        for user in users:
            with self.subTest(user=user.role):
                self.client.force_authenticate(user)
                url = reverse('guest-detail', kwargs={'pk': self.guest1.pk})
                response = self.client.get(url)
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                self.assertEqual(response.data['email'], self.guest1.email)

    def test_retrieve_nonexistent_guest_returns_404(self):
        self.client.force_authenticate(self.admin)
        url = reverse('guest-detail', kwargs={'pk': 99999})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_admin_can_create_guest(self):
        self.client.force_authenticate(self.admin)
        user_data = {
            'email': 'guest3@example.com',
            'first_name': 'Guest',
            'last_name': 'Three',
            'phone_number': '+79999999999',
            'password': 'GoodPassword432+',
        }
        response = self.client.post(self.base_url, user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        guest = User.objects.filter(email=user_data['email']).first()
        self.assertIsNotNone(guest)
        self.assertTrue(hasattr(guest, 'guest'))
        self.assertEqual(guest.first_name, user_data['first_name'])
        self.assertEqual(guest.last_name, user_data['last_name'])
        self.assertEqual(guest.phone_number, user_data['phone_number'])
        self.assertTrue(guest.check_password(user_data['password']))

    def test_moderator_cannot_create_guest(self):
        user_data = {
            'email': 'guest3@example.com',
            'first_name': 'Guest',
            'last_name': 'Three',
            'phone_number': '+79999999999',
            'password': 'GoodPassword432+',
        }
        self.client.force_authenticate(self.moderator)
        response = self.client.post(self.base_url, user_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(User.objects.filter(email=user_data['email']).exists())

    def test_create_guest_with_invalid_data_returns_400(self):
        wrong_email = {
            'email': 'not-an-email',
            'first_name': 'Guest',
            'last_name': 'Three',
            'phone_number': '+79999999999',
            'password': 'GoodPassword432+',
        }
        wrong_phone = {
            'email': 'guest4@example.com',
            'first_name': 'Guest',
            'last_name': 'Four',
            'phone_number': '12345789',
            'password': 'GoodPassword432+',
        }
        no_email = {
            'first_name': 'Guest',
            'last_name': 'Five',
            'phone_number': '+79999999999',
            'password': 'GoodPassword432+',
        }
        no_phone = {
            'email': 'guest6@example.com',
            'first_name': 'Guest',
            'last_name': 'Six',
            'password': 'GoodPassword432+',
        }
        no_last_name = {
            'email': 'guest7@example.com',
            'first_name': 'Guest',
            'phone_number': '+79999999999',
            'password': 'GoodPassword432+',
        }
        self.client.force_authenticate(self.admin)

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

    def test_admin_can_delete_guest(self):
        self.client.force_authenticate(self.admin)
        url = reverse('guest-detail', kwargs={'pk': self.guest1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.guest1.pk).exists())

    def test_modetator_cannot_delete_guest(self):
        self.client.force_authenticate(self.moderator)
        url = reverse('guest-detail', kwargs={'pk': self.guest1.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_update_guest(self):
        self.client.force_authenticate(self.admin)
        url = reverse('guest-detail', kwargs={'pk': self.guest1.pk})
        response = self.client.patch(url, {'first_name': 'NewName'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.guest1.refresh_from_db()
        self.assertEqual(self.guest1.first_name, 'NewName')

    def test_moderator_cannot_update_guest(self):
        self.client.force_authenticate(self.moderator)
        url = reverse('guest-detail', kwargs={'pk': self.guest1.pk})
        response = self.client.patch(url, {'first_name': 'NewName'})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
