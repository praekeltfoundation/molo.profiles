from datetime import date

from django.conf.urls import patterns, url, include
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, Client

from molo.profiles.forms import RegistrationForm


urlpatterns = patterns(
    '',
    url(r'^profiles/',
        include('molo.profiles.urls',
                namespace='molo.profiles',
                app_name='molo.profiles')),
)


@override_settings(ROOT_URLCONF='molo.profiles.tests.test_views')
class ViewTest(TestCase):

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
