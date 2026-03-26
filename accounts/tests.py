from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Profile

User = get_user_model()


class UserModelTest(TestCase):

    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_profile_created_on_user_creation(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, Profile)


class RegistrationViewTest(TestCase):

    def test_registration_page_loads(self):
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/register-page.html')

    def test_registration_with_valid_data(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

        user = User.objects.filter(email='newuser@example.com').first()
        self.assertIsNotNone(user)

    def test_registration_with_invalid_email(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass123',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='invalid-email').exists())

    def test_registration_with_mismatched_passwords(self):
        response = self.client.post(reverse('accounts:register'), {
            'email': 'newuser@example.com',
            'password1': 'testpass123',
            'password2': 'differentpass',
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(email='newuser@example.com').exists())


class LoginViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_email_verified = True
        self.user.save()

    def test_login_page_loads(self):
        response = self.client.get(reverse('accounts:login'))
        self.assertEqual(response.status_code, 200)

    def test_login_with_valid_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': 'testpass123',
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_invalid_credentials(self):
        response = self.client.post(reverse('accounts:login'), {
            'username': 'test@example.com',
            'password': 'wrongpassword',
        })
        self.assertEqual(response.status_code, 200)


class ProfileViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.user.is_active = True
        self.user.is_email_verified = True
        self.user.save()

    def test_profile_detail_requires_login(self):
        response = self.client.get(
            reverse('accounts:profile-details',
                    kwargs={'pk': self.user.profile.pk})
        )
        self.assertEqual(response.status_code, 302)

    def test_authenticated_user_can_view_profile(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse('accounts:profile-details',
                    kwargs={'pk': self.user.profile.pk})
        )
        self.assertEqual(response.status_code, 200)

