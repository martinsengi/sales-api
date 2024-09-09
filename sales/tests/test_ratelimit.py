from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


class RateLimitingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='apiuser', password='apiuserpass', is_staff=True
        )

        self.token_obtain_url = reverse('token_obtain_pair')
        self.token_refresh_url = reverse('token_refresh')

    def test_jwt_token_obtain_rate_limit(self):
        cache.clear()

        for _ in range(10):
            response = self.client.post(
                self.token_obtain_url,
                {'username': 'apiuser', 'password': 'apiuserpass'},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.token_obtain_url,
            {'username': 'apiuser', 'password': 'apiuserpass'},
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_jwt_token_refresh_rate_limit(self):
        cache.clear()

        response = self.client.post(
            self.token_obtain_url,
            {'username': 'apiuser', 'password': 'apiuserpass'},
        )
        refresh_token = response.data['refresh']

        for _ in range(20):
            response = self.client.post(
                self.token_refresh_url,
                {'refresh': refresh_token},
            )
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.post(
            self.token_refresh_url,
            {'refresh': refresh_token},
        )
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

    def test_user_rate_limit(self):
        cache.clear()

        token = RefreshToken.for_user(self.user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        for _ in range(2000):
            response = self.client.get(reverse('sales-data-list'))
            self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.get(reverse('sales-data-list'))
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        retry_after_seconds = int(response.headers['Retry-After'])
        self.assertTrue(3500 < retry_after_seconds <= 3600)  # Verify rate limit duration is an hour
