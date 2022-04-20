from django.contrib.auth import authenticate
from django.test import TestCase
from django.test.utils import override_settings
from icmo_users.models import IcmoUser


class IcmoUserTestCase(TestCase):
    def setUp(self):
        u = IcmoUser.objects.create(email = 'matthew@ragingbits.com')

    @override_settings(AUTH_USER_MODEL='icmo_users.IcmoUser')
    def test_user_exists(self):
        u = IcmoUser.objects.get(email = 'matthew@ragingbits.com')
        self.assertEqual(u.email, 'matthew@ragingbits.com')

    @override_settings(AUTH_USER_MODEL='icmo_users.IcmoUser')
    def test_user_set_password(self):
        u = IcmoUser.objects.get(email = 'matthew@ragingbits.com')
        u.set_password('password123#')
        u.save()
        u = IcmoUser.objects.get(email = 'matthew@ragingbits.com')
        self.assertIsNotNone(u.password)

    @override_settings(AUTH_USER_MODEL='icmo_users.IcmoUser')
    def test_user_auth(self):
        u = IcmoUser.objects.get(email = 'matthew@ragingbits.com')
        u.set_password('password123#')
        u.save()
        au = authenticate(  username = 'matthew@ragingbits.com',
                            password='password123#')
        self.assertEqual(au.email, 'matthew@ragingbits.com')

    @override_settings(AUTH_USER_MODEL='icmo_users.IcmoUser')
    def test_user_deactivate(self):
        u = IcmoUser.objects.get(email = 'matthew@ragingbits.com')
        u.deactivate()
        self.assertFalse(u.is_active)
