from datetime import date

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, Client

from molo.profiles.forms import (
    RegistrationForm, EditProfileForm, ProfilePasswordChangeForm)
from molo.profiles.models import UserProfile


urlpatterns = patterns(
    '',
    url(r'^profiles/',
        include('molo.profiles.urls',
                namespace='molo.profiles',
                app_name='molo.profiles')),
)


@override_settings(ROOT_URLCONF='molo.profiles.tests.test_views')
class RegistrationViewTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_register_view(self):
        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertTrue(isinstance(response.context['form'], RegistrationForm))

    def test_register_view_invalid_form(self):
        # NOTE: empty form submission
        response = self.client.post(reverse('molo.profiles:user_register'), {
        })
        self.assertFormError(
            response, 'form', 'username', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'])
        self.assertFormError(
            response, 'form', 'date_of_birth', ['This field is required.'])

    def test_register_sets_dob(self):
        self.assertFalse(User.objects.filter(username='testing').exists())
        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing',
            'password': '1234',
            'date_of_birth': '1980-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testing')
        self.assertEqual(user.profile.date_of_birth, date(1980, 1, 1))

    def test_logout(self):
        response = self.client.get('%s?next=%s' % (
            reverse('molo.profiles:auth_logout'),
            reverse('molo.profiles:user_register')))
        self.assertRedirects(response, reverse('molo.profiles:user_register'))


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views',
    TEMPLATE_CONTEXT_PROCESSORS=settings.TEMPLATE_CONTEXT_PROCESSORS + (
        'molo.profiles.context_processors.get_profile_data',
    ))
class MyProfileViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()

    def test_view(self):
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'tester')
        self.assertContains(response, 'The Alias')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class MyProfileEditTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')

    def test_view(self):
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'alias': 'foo'
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).alias,
                         'foo')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class ProfilePasswordChangeViewTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='0000')
        self.client = Client()
        self.client.login(username='tester', password='0000')

    def test_view(self):
        response = self.client.get(
            reverse('molo.profiles:profile_password_change'))
        form = response.context['form']
        self.assertTrue(isinstance(form, ProfilePasswordChangeForm))

    def test_update_invalid_old_password(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '1234',
                'new_password': '4567',
                'confirm_password': '4567',
            })
        [message] = response.context['messages']
        self.assertEqual(message.message, 'The old password is incorrect.')

    def test_update_passwords_not_matching(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '0000',
                'new_password': '1234',
                'confirm_password': '4567',
            })
        form = response.context['form']
        [error] = form.non_field_errors().as_data()
        self.assertEqual(error.message, 'New passwords do not match.')

    def test_update_passwords(self):
        response = self.client.post(
            reverse('molo.profiles:profile_password_change'), {
                'old_password': '0000',
                'new_password': '1234',
                'confirm_password': '1234',
            })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        # Avoid cache by loading from db
        user = User.objects.get(pk=self.user.pk)
        self.assertTrue(user.check_password('1234'))
