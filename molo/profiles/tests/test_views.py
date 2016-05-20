from datetime import date

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings, Client

from molo.profiles.forms import (
    RegistrationForm, EditProfileForm, ProfilePasswordChangeForm)
from molo.profiles.models import UserProfile
from molo.core.tests.base import MoloTestCaseMixin

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

urlpatterns = patterns(
    '',
    url(r'', include('testapp.urls')),
    url(r'^profiles/',
        include('molo.profiles.urls',
                namespace='molo.profiles',
                app_name='molo.profiles')),
)


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views', LOGIN_URL='/login/')
class RegistrationViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.client = Client()
        self.mk_main()

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

    def test_register_auto_login(self):
        # Not logged in, redirects to login page
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response['Location'],
            '/login/?next=/profiles/edit/myprofile/')

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing',
            'password': '1234',
            'terms_and_conditions': True

        })

        # After registration, doesn't redirect
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertEqual(response.status_code, 200)

    def test_logout(self):
        response = self.client.get('%s?next=%s' % (
            reverse('molo.profiles:auth_logout'),
            reverse('molo.profiles:user_register')))
        self.assertRedirects(response, reverse('molo.profiles:user_register'))

    def test_login(self):
        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'Forgotten your password')

    def test_mobile_number_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'Enter your mobile number')

        profile_settings.show_mobile_number_field = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'Enter your mobile number')

    def test_email_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'Enter your email')

        profile_settings.show_email_field = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'Enter your email')

    def test_mobile_number_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['This field is required.'])

    def test_email_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'email', ['This field is required.'])

    def test_mobile_num_is_required_but_show_mobile_num_field_is_false(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = False
        profile_settings.mobile_number_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

    def test_email_is_required_but_show_email_field_is_false(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = False
        profile_settings.email_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_mobile_number(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '0785577743'
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['Enter a valid phone number.'])

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '27785577743'
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['Enter a valid phone number.'])

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+2785577743'
        })
        self.assertFormError(
            response, 'form', 'mobile_number', ['Enter a valid phone number.'])

    def test_invalid_email(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'email': 'example@'
        })
        self.assertFormError(
            response, 'form', 'email', ['Enter a valid email address.'])

    def test_valid_mobile_number(self):
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+27784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')

    def test_valid_email(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().user.email,
                         'example@foo.com')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class RegistrationDone(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')
        self.mk_main()

    def test_date_of_birth(self):
        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.date_of_birth, date(2000, 1, 1))


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views',
    TEMPLATE_CONTEXT_PROCESSORS=settings.TEMPLATE_CONTEXT_PROCESSORS + [
        'molo.profiles.context_processors.get_profile_data',
    ])
class MyProfileViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()
        self.mk_main()

    def test_view(self):
        self.client.login(username='tester', password='tester')
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'tester')
        self.assertContains(response, 'The Alias')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class MyProfileEditTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')
        self.mk_main()

    def test_view(self):
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update_alias_only(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {
            'alias': 'foo'
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).alias,
                         'foo')

    # Test for update with dob only is in ProfileDateOfBirthEditTest

    def test_update_no_input(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {})
        self.assertFormError(
            response, 'form', None, ['Please enter a new value.'])

    def test_update_alias_and_dob(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {
            'alias': 'foo',
            'date_of_birth': '2000-01-01'
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).alias,
                         'foo')
        self.assertEqual(UserProfile.objects.get(user=self.user).date_of_birth,
                         date(2000, 1, 1))

    def test_update_mobile_number(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'mobile_number': '+27788888813'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).mobile_number,
                         '+27788888813')

    def test_update_email(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': 'example@foo.com'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).user.email,
                         'example@foo.com')


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class ProfileDateOfBirthEditTest(MoloTestCaseMixin, TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.client = Client()
        self.client.login(username='tester', password='tester')
        self.mk_main()

    def test_view(self):
        response = self.client.get(
            reverse('molo.profiles:edit_my_profile'))
        form = response.context['form']
        self.assertTrue(isinstance(form, EditProfileForm))

    def test_update_date_of_birth(self):
        response = self.client.post(reverse(
            'molo.profiles:edit_my_profile'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).date_of_birth,
                         date(2000, 1, 1))


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
