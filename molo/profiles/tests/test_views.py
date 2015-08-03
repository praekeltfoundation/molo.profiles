from datetime import date

from django.contrib.auth.models import User
from django.test import TestCase
from django.test.client import Client
from django.core.urlresolvers import reverse

from molo.profiles.forms import RegistrationForm


class ViewTest(TestCase):

    urls = 'molo.profiles.urls'

    def setUp(self):
        self.client = Client()

    def test_register_view(self):
        response = self.client.get(reverse('user_register'))
        self.assertTrue(isinstance(response.context['form'], RegistrationForm))

    def test_register_sets_dob(self):
        self.assertFalse(User.objects.filter(username='testing').exists())
        response = self.client.post(reverse('user_register'), {
            'username': 'testing',
            'password': '1234',
            'date_of_birth': '1980-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='testing')
        self.assertEqual(user.profile.date_of_birth, date(1980, 1, 1))
