from collections import OrderedDict

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from ..models import User, ReferralCode


class UserRegisterViewTestCase(APITestCase):
    def test_register_new_user(self):
        url = reverse('register')
        data = {'username': 'vladimir', 'password': 'password666', 'email': 'vladimir@gmail.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='vladimir').exists())

    def test_register_existing_user(self):
        User.objects.create_user(username='vladimir', password='password666')

        url = reverse('register')
        data = {'username': 'vladimir', 'password': 'password666', 'email': 'ialreadyexist@gmail.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['error'], 'User with this username already exists!')


class UserLoginViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vladimir', password='password666')

    def test_login(self):
        url = reverse('login')
        data = {'username': 'vladimir', 'password': 'password666'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access_token', response.data)
        self.assertIn('refresh_token', response.data)

    def test_login_with_invalid_credentials(self):
        url = reverse('login')
        data = {'username': 'not___vladimir', 'password': 'not___password666'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['detail'], 'Unable to log in with provided credentials!')


class ReferralCodeViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vladimir', password='password666')
        self.client.force_authenticate(user=self.user)

    def test_create_referral_code(self):
        url = reverse('referral_code_use')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('code', response.data)

    def test_get_referral_code(self):
        url = reverse('referral_code_use')
        create_code_response = self.client.post(url)
        get_code_response = self.client.get(url)
        self.assertEqual(get_code_response.status_code, status.HTTP_200_OK)
        self.assertEqual(create_code_response.data.get('code'), get_code_response.data.get('code'))

    def test_delete_referral_code(self):
        url = reverse('referral_code_use')
        self.client.post(url)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class ReferralCodeByEmailTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vladimir', password='password666')
        self.client.force_authenticate(user=self.user)

    def test_get_code_by_email(self):
        test_referer = User.objects.create_user(
            username='harrypotter',
            password='harrypotter',
            email='harrypotter@gmail.com')
        ReferralCode.objects.create(user=test_referer)
        url = reverse('referral_code_get_by_email', kwargs={'email': 'harrypotter@gmail.com'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('user'), test_referer.id)


class UserReferralListViewTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='vladimir', password='password666')
        self.client.force_authenticate(user=self.user)

    def test_get_user_referals(self):
        referral_one = User.objects.create_user(username='referral1', password='ref1', referrer=self.user)
        referral_two = User.objects.create_user(username='referral2', password='ref2', referrer=self.user)
        url = reverse('check_referrals_by_id', kwargs={'pk': self.user.id})
        response = self.client.get(url)
        response_data_sorted = sorted(response.data, key=lambda x: x['username'])
        expected_data_sorted = sorted([{'username': 'referral1'}, {'username': 'referral2'}], key=lambda x: x['username'])
        self.assertEqual(response_data_sorted, expected_data_sorted)


