# -*- coding: utf-8 -*-
from datetime import date

from django.conf.urls import patterns, url, include
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.urlresolvers import reverse
from django.http import QueryDict
from django.test import TestCase, override_settings, Client

from molo.profiles.forms import (
    RegistrationForm, EditProfileForm,
    ProfilePasswordChangeForm, ForgotPasswordForm)
from molo.profiles.models import (
    SecurityQuestion,
    SecurityAnswer,
    UserProfile,
    SecurityQuestionIndexPage,
)
from molo.core.models import (
    PageTranslation, SiteLanguage, Main, FooterPage)

from molo.core.tests.base import MoloTestCaseMixin

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

from bs4 import BeautifulSoup

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
        # Creates Main language
        SiteLanguage.objects.create(locale='en')

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

    def test_warning_message_shown_in_wagtail_if_no_country_code(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.save()

        User.objects.create_superuser(
            username='testuser', password='password', email='test@email.com')
        self.client.login(username='testuser', password='password')

        response = self.client.get(reverse('wagtailadmin_home'))
        self.assertContains(
            response, 'You have activated mobile number in registration form,'
            ' but you have not added a country calling code for this site.')

    def test_mobile_number_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR MOBILE NUMBER')

        profile_settings.show_mobile_number_field = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR MOBILE NUMBER')

        profile_settings.country_code = '+27'
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'ENTER YOUR MOBILE NUMBER')

    def test_email_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'ENTER YOUR EMAIL ADDRESS')

        profile_settings.show_email_field = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'ENTER YOUR EMAIL ADDRESS')

    def test_date_of_birth_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'SELECT DATE OF BIRTH')

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'SELECT DATE OF BIRTH')

    def test_display_name_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'CHOOSE A DISPLAY NAME')

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'CHOOSE A DISPLAY NAME')

    def test_gender_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'I IDENTIFY MY GENDER AS:')

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'I IDENTIFY MY GENDER AS:')

    def test_location_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'WHERE DO YOU LIVE?')

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'WHERE DO YOU LIVE?')

    def test_education_level_field_exists_in_registration_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertNotContains(response, 'WHAT IS YOUR HIGHEST '
                                         'LEVEL OF EDUCATION?')

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, 'WHAT IS YOUR HIGHEST '
                                      'LEVEL OF EDUCATION?')

    def test_mobile_number_field_is_optional(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = False
        profile_settings.country_code = '+27'
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

    def test_mobile_number_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
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

    def test_display_name_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.display_name_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'alias', ['This field is required.'])

    def test_display_name_is_not_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = True
        profile_settings.display_name_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_date_of_birth_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = True
        profile_settings.dob_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'date_of_birth', ['This field is required.'])

    def test_date_of_birth_field_not_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.dob_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertEqual(response.status_code, 302)

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_gender_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])

    def test_gender_not_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = True
        profile_settings.gender_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_location_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.location_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'location', ['This field is required.'])

    def test_location_not_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = True
        profile_settings.location_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

    def test_education_level_field_is_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = True
        profile_settings.activate_education_level_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'foo',
            'password': '1234',
            'terms_and_conditions': True
        })
        self.assertFormError(
            response, 'form', 'education_level', ['This field is required.'])

    def test_education_level_not_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = True
        profile_settings.activate_education_level_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'terms_and_conditions': True
        })

        # When successful
        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Thank you for joining!')

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
        profile_settings.country_code = '+27'
        profile_settings.save()

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
        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+089885577743'
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
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '0784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')

    def test_valid_mobile_number_edit_profile(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '0784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')
        self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'mobile_number': '0784500004',
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500004')

    def test_valid_mobile_number_with_plus(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '+27784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')
        self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'mobile_number': '0784500004',
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500004')

    def test_valid_mobile_number_without_zero(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test',
            'password': '1234',
            'mobile_number': '784500003',
            'terms_and_conditions': True
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500003')
        self.client.post(reverse('molo.profiles:edit_my_profile'), {
            'mobile_number': '+27784500005',
        })
        self.assertEqual(UserProfile.objects.get().mobile_number,
                         '+27784500005')

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

    def test_email_or_phone_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)

        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.prevent_phone_number_in_username = True
        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test@test.com',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "Sorry, but that is an invalid " \
                                      "username. Please don&#39;t use " \
                                      "your phone number or email address " \
                                      "in your username."

        self.assertContains(response, expected_validation_message)

    def test_email_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)

        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'test@test.com',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#39;t use" \
                                      " your email address in your" \
                                      " username."

        self.assertContains(response, expected_validation_message)

    def test_ascii_code_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)

        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.prevent_email_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'A bad username 😁',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "This value must contain only letters,"\
                                      " numbers and underscores."
        self.assertContains(response, expected_validation_message)

    def test_phone_number_not_allowed_in_username(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)

        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.prevent_phone_number_in_username = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:user_register'), {
            'username': '021123123123',
            'password': '1234',
            'email': 'example@foo.com',
            'terms_and_conditions': True
        })

        expected_validation_message = "Sorry, but that is an invalid" \
                                      " username. Please don&#39;t use" \
                                      " your phone number in your username."

        self.assertContains(response, expected_validation_message)

    def test_security_questions(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)

        SecurityQuestion.objects.create(
            title="What is your name?",
            slug="what-is-your-name",
            path="0002",
            depth=1,
        )

        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.show_security_question_fields = True
        profile_settings.security_questions_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))
        self.assertContains(response, "What is your name")

        # register with security questions
        response = self.client.post(
            reverse("molo.profiles:user_register"),
            {
                "username": "tester",
                "password": "0000",
                "question_0": "answer",
                'terms_and_conditions': True
            },
            follow=True
        )
        self.assertEqual(response.status_code, 200)


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

    def test_date_of_birth_on_done(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_dob = True
        profile_settings.capture_dob_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, '<p class="profiles__description">'
                            'Let us know more about yourself '
                            'to get access to exclusive content.</p>')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'date_of_birth': '2000-01-01',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.date_of_birth, date(2000, 1, 1))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_display_name_on_done(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_display_name = True
        profile_settings.capture_display_name_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, '<p class="profiles__description">'
                            'Let us know more about yourself '
                            'to get access to exclusive content.</p>')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'alias': 'foo',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.alias, ('foo'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_gender_on_done(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_gender = True
        profile_settings.capture_gender_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, '<p class="profiles__description">'
                            'Let us know more about yourself '
                            'to get access to exclusive content.</p>')
        self.assertContains(response, 'Thank you for joining!')

        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'gender': 'male',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.gender, ('male'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_location_on_done(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_location = True
        profile_settings.capture_location_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, '<p class="profiles__description">'
                            'Let us know more about yourself '
                            'to get access to exclusive content.</p>')
        self.assertContains(response, 'Thank you for joining!')
        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'location': 'mlazi',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.location, ('mlazi'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_education_level_on_done(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_education_level = True
        profile_settings.capture_education_level_on_reg = False
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:registration_done'))
        self.assertContains(response, '<p class="profiles__description">'
                            'Let us know more about yourself '
                            'to get access to exclusive content.</p>')
        self.assertContains(response, 'Thank you for joining!')
        response = self.client.post(reverse(
            'molo.profiles:registration_done'), {
            'education_level': 'level 0',
        })
        self.assertEqual(response.status_code, 302)
        user = User.objects.get(username='tester')
        self.assertEqual(user.profile.education_level, ('level 0'))

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class TestTermsAndConditions(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.footer = FooterPage(
            title='terms and conditions', slug='terms-and-conditions')
        self.footer_index.add_child(instance=self.footer)

    def test_terms_and_conditions_linked_to_terms_and_conditions_page(self):
        response = self.client.get(reverse('molo.profiles:user_register'))

        self.assertNotContains(
            response,
            '<a href="/footer-pages/terms-and-conditions/"'
            ' for="id_terms_and_conditions" class="profiles__terms">'
            'I accept the Terms and Conditions</a>')
        self.assertContains(
            response,
            '<label for="id_terms_and_conditions"'
            ' class="profiles__terms">'
            'I accept the Terms and Conditions</label>')

        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.terms_and_conditions = self.footer
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:user_register'))

        self.assertContains(
            response,
            '<a href="/footer-pages/terms-and-conditions/"'
            ' for="id_terms_and_conditions" class="profiles__terms">'
            'I accept the Terms and Conditions</a>')


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
    ROOT_URLCONF='molo.profiles.tests.test_views', LOGIN_URL='/login/')
class LoginTestView(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='1234')
        # Update the userprofile without touching (and caching) user.profile
        UserProfile.objects.filter(user=self.user).update(alias='The Alias')
        self.client = Client()
        self.mk_main()

    def test_login_success(self):
        self.client.login(username='tester', password='1234')

        response = self.client.get(reverse('molo.profiles:auth_login'))
        self.assertContains(response, 'value="/profiles/login-success/"')

        response = self.client.get(reverse('molo.profiles:login_success'))
        self.assertContains(response, 'Welcome Back!')

    def test_login_success_redirects(self):
        self.client.login(username='tester', password='1234')

        response = self.client.post(
            reverse('molo.profiles:auth_login'),
            data={'username': 'tester', 'password': '1234',
                  'next': '/profiles/login-success/'},
            follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response, reverse('molo.profiles:login_success'))


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

    def test_gender_field_exists_in_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update your gender:')

        profile_settings.activate_gender = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'Update your gender:')

    def test_location_field_exists_in_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update where you live:')

        profile_settings.activate_location = True
        profile_settings.location_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'Update where you live:')

    def test_education_level_field_exists_in_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertNotContains(response, 'Update your Education Level:')

        profile_settings.activate_education_level = True
        profile_settings.activate_education_level_required = True
        profile_settings.save()

        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'Update your Education Level:')

    def test_email_showing_in_edit_view(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()
        response = self.client.get(reverse('molo.profiles:edit_my_profile'))
        self.assertContains(response, 'tester@example.com')

    # Test for update with dob only is in ProfileDateOfBirthEditTest

    def test_update_no_input(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'),
                                    {})
        self.assertEquals(response.status_code, 302)

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

    def test_update_gender(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.activate_gender = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).gender,
                         'male')

    def test_update_location(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.activate_location = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': 'mlazi'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).location,
                         'mlazi')

    def test_update_education_level(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.activate_education_level = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': 'level0'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(
            UserProfile.objects.get(user=self.user).education_level,
            'level0')

    def test_update_email(self):
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': 'example@foo.com'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))
        self.assertEqual(UserProfile.objects.get(user=self.user).user.email,
                         'example@foo.com')

    def test_update_when_email_optional(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = True
        profile_settings.email_required = False
        profile_settings.save()
        # user removes their mobile number
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': ''})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

    def test_update_when_email_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_email_field = True
        profile_settings.email_required = True
        profile_settings.save()
        # user removes their mobile number
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'email': ''})
        self.assertFormError(
            response, 'form', 'email', ['This field is required.'])

    def test_update_when_mobile_number_optional(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = False
        profile_settings.country_code = '+27'
        profile_settings.save()
        # user removes their mobile number
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'mobile_number': ''})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

    def test_update_when_mobile_number_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.show_mobile_number_field = True
        profile_settings.mobile_number_required = True
        profile_settings.country_code = '+27'
        profile_settings.save()
        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'mobile_number': ''})
        self.assertFormError(
            response, 'form', 'mobile_number', ['This field is required.'])

    def test_gender_field_is_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_gender = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': ''})
        self.assertFormError(
            response, 'form', 'gender', ['This field is required.'])

    def test_gender_not_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_gender = True
        profile_settings.gender_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': ''})

        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'male')

    def test_location_field_is_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_location = True
        profile_settings.location_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': ''})
        self.assertFormError(
            response, 'form', 'location', ['This field is required.'])

    def test_location_not_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_location = True
        profile_settings.location_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': ''})

        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'location': 'mlazi'})
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'mlazi')

    def test_education_level_field_is_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_education_level = True
        profile_settings.activate_education_level_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': ''})
        self.assertFormError(
            response, 'form', 'education_level', ['This field is required.'])

    def test_education_level_not_required_on_edit_form(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        profile_settings.activate_education_level = True
        profile_settings.activate_education_level_required = False
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': ''})

        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'education_level': 'level0'})
        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'level0')

    def test_gender_required_location_not_required(self):
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        profile_settings.activate_location = True
        profile_settings.activate_gender = True
        profile_settings.gender_required = True
        profile_settings.save()

        response = self.client.post(reverse('molo.profiles:edit_my_profile'), {
                                    'gender': 'male'})
        self.assertRedirects(
            response, reverse('molo.profiles:view_my_profile'))

        response = self.client.get(reverse('molo.profiles:view_my_profile'))
        self.assertContains(response, 'male')


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
class ProfilePasswordChangeViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
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


@override_settings(
    ROOT_URLCONF="molo.profiles.tests.test_views",
)
class ForgotPasswordViewTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")
        # Creates Main language
        SiteLanguage.objects.create(locale='en')

        # create a few security questions
        q1 = SecurityQuestion.objects.create(
            title="How old are you?",
            slug="how-old-are-you",
            path="0002",
            depth=1,
        )

        # create answers for this user
        self.a1 = SecurityAnswer.objects.create(
            user=self.user.profile, question=q1, answer="20"
        )

    def test_view(self):
        response = self.client.get(
            reverse("molo.profiles:forgot_password"))
        form = response.context["form"]
        self.assertTrue(isinstance(form, ForgotPasswordForm))

    def test_unidentified_user_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "bogus",
                "question_0": "20",
            }
        )
        self.failUnless(error_message in response.content)

    def test_suspended_user_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        self.user.is_active = False
        self.user.save()
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            }
        )
        self.failUnless(error_message in response.content)
        self.user.is_active = True
        self.user.save()

    def test_incorrect_security_answer_gets_error(self):
        error_message = "The username and security question(s) combination " \
                        "do not match."
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "21",
            }
        )
        self.failUnless(error_message in response.content)

    def test_too_many_retries_result_in_error(self):
        error_message = "Too many attempts"
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']

        # post more times than the set number of retries
        for i in range(profile_settings.password_recovery_retries + 5):
            response = self.client.post(
                reverse("molo.profiles:forgot_password"), {
                    "username": "bogus",
                    "question_0": "20",
                }
            )

        self.failUnless(error_message in response.content)

    def test_correct_username_and_answer_results_in_redirect(self):
        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            },
            follow=True
        )
        self.assertContains(response, "Reset PIN")


class TranslatedSecurityQuestionsTest(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.questions_section = self.mk_section(
            self.section_index, title='Security Questions')

        # Creates Main language
        SiteLanguage.objects.create(locale="en")

        # Creates translation Language
        self.french = SiteLanguage.objects.create(locale="fr")

        # create a few security questions
        self.q1 = SecurityQuestion.objects.create(
            title="How old are you?",
            slug="how-old-are-you",
            path="0002",
            depth=1,
        )

    def test_translated_question_appears_on_registration(self):
        # make translation for the security question
        fr_question = SecurityQuestion.objects.create(
            title="How old are you in french",
            slug="how-old-are-you-in-french",
            path="0003",
            depth=1,
        )
        language_relation = fr_question.languages.first()
        language_relation.language = self.french
        language_relation.save()
        fr_question.save_revision().publish()
        PageTranslation.objects.get_or_create(
            page=self.q1, translated_page=fr_question)

        self.client.get('/locale/fr/')
        response = self.client.get(reverse("molo.profiles:forgot_password"))
        self.assertContains(response, "How old are you in french")

        # switch locale to english and check that the english question
        # is asked
        self.client.get('/locale/en/')
        response = self.client.get(reverse("molo.profiles:forgot_password"))
        self.failIf("How old are you in french" in response.content)


class ResetPasswordViewTest(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.client = Client()
        self.user = User.objects.create_user(
            username="tester",
            email="tester@example.com",
            password="0000")

        # Creates Main language
        SiteLanguage.objects.create(locale='en')

        # create a few security questions
        q1 = SecurityQuestion.objects.create(
            title="How old are you?",
            slug="how-old-are-you",
            path="0002",
            depth=1,
        )

        # create answers for this user
        self.a1 = SecurityAnswer.objects.create(
            user=self.user.profile, question=q1, answer="20"
        )

    def proceed_to_reset_password_page(self):
        expected_token = default_token_generator.make_token(self.user)
        expected_query_params = QueryDict(mutable=True)
        expected_query_params["user"] = self.user.username
        expected_query_params["token"] = expected_token
        expected_redirect_url = "{0}?{1}".format(
            reverse("molo.profiles:reset_password"),
            expected_query_params.urlencode()
        )

        response = self.client.post(
            reverse("molo.profiles:forgot_password"), {
                "username": "tester",
                "question_0": "20",
            }
        )

        self.assertRedirects(response, expected_redirect_url)

        return expected_token, expected_redirect_url

    def test_reset_password_view_pin_mismatch(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "4321"
        })

        self.assertContains(response, "The two PINs that you entered do not "
                                      "match. Please try again.")

    def test_reset_password_view_requires_query_params(self):
        response = self.client.get(reverse("molo.profiles:reset_password"))
        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_username(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": "invalid",
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_inactive_user(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        self.user.is_active = False
        self.user.save()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_reset_password_view_invalid_token(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": "invalid",
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertEqual(403, response.status_code)

    def test_happy_path(self):
        expected_token, expected_redirect_url = \
            self.proceed_to_reset_password_page()

        response = self.client.post(expected_redirect_url, {
            "username": self.user.username,
            "token": expected_token,
            "password": "1234",
            "confirm_password": "1234"
        })

        self.assertRedirects(
            response,
            reverse("molo.profiles:reset_password_success")
        )

        self.assertTrue(
            self.client.login(username="tester", password="1234")
        )


@override_settings(
    ROOT_URLCONF='molo.profiles.tests.test_views')
class TestDeleteButtonRemoved(TestCase, MoloTestCaseMixin):

    def setUp(self):
        self.mk_main()
        self.english = SiteLanguage.objects.create(locale='en')
        self.login()

        self.security_question_index = SecurityQuestionIndexPage(
            title='Security Questions',
            slug='security-questions')
        self.main.add_child(instance=self.security_question_index)
        self.security_question_index.save_revision().publish()

    def test_delete_button_removed_for_sec_ques_index_page_in_main(self):
        main_page = Main.objects.first()

        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(main_page.pk)))
        self.assertEquals(response.status_code, 200)

        security_q_index_page_title = (
            SecurityQuestionIndexPage.objects.first().title)

        soup = BeautifulSoup(response.content, 'html.parser')
        index_page_rows = soup.find_all('tbody')[0].find_all('tr')

        for row in index_page_rows:
            if row.h2.a.string == security_q_index_page_title:
                self.assertTrue(row.find('a', string='Edit'))
                self.assertFalse(row.find('a', string='Delete'))

    def test_delete_button_removed_from_dropdown_menu_main(self):
        security_q_index_page = SecurityQuestionIndexPage.objects.first()

        response = self.client.get('/admin/pages/{0}/'
                                   .format(str(security_q_index_page.pk)))
        self.assertEquals(response.status_code, 200)

        delete_link = ('<a href="/admin/pages/{0}/delete/" '
                       'title="Delete this page" class="u-link '
                       'is-live ">Delete</a>'
                       .format(str(security_q_index_page.pk)))
        self.assertNotContains(response, delete_link, html=True)

    def test_delete_button_removed_in_edit_menu(self):
        security_q_index_page = SecurityQuestionIndexPage.objects.first()

        response = self.client.get('/admin/pages/{0}/edit/'
                                   .format(str(security_q_index_page.pk)))
        self.assertEquals(response.status_code, 200)

        delete_button = ('<li><a href="/admin/pages/{0}/delete/" '
                         'class="shortcut">Delete</a></li>'
                         .format(str(security_q_index_page.pk)))
        self.assertNotContains(response, delete_button, html=True)
