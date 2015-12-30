from django.test import TestCase
from django.contrib.auth.models import User
from django.test import Client
from django.core.urlresolvers import reverse


class SetTokenCookieDecoratorTestCase(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            'test',
            'test@test.com',
            'password'
        )
        user.is_active = True
        user.save()

    def test_set_token_cookie_without_sso(self):
        client = Client()
        response = client.post(reverse('login'), {
            'username': 'test',
            'password': 'password'
        })
        self.assertIn('authenticated_token', response.cookies)
