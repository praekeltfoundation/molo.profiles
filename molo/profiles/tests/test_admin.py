# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import cgi
import sys
from datetime import date

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.test.client import Client
from django.core.urlresolvers import reverse

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import Main, Languages, SiteLanguageRelation
from molo.profiles.admin import ProfileUserAdmin, download_as_csv
from molo.profiles.models import UserProfile

if sys.version_info[0] < 3:
    from backports import csv
else:
    import csv


class ModelsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)

    def assert_csv_download(self, response, filename, rows):
        self.assertEquals(response.status_code, 200)

        self.assertEquals(response['Content-Type'], 'text/csv')

        disposition, params = cgi.parse_header(response['Content-Disposition'])
        self.assertEquals(disposition, 'attachment')
        self.assertEquals(params, {'filename': filename})

        response_lines = response.content.decode('utf-8').split('\r\n')
        self.assertEquals(response_lines.pop(), '')

        self.assertEquals([row for row in csv.reader(response_lines)], rows)

    def test_download_csv(self):
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.mobile_number = '+27784667723'
        profile.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = self.user.date_joined.strftime("%Y-%m-%d %H:%M")

        self.assert_csv_download(response, 'export.csv', [
            ['username', 'email', 'first_name', 'last_name', 'is_staff',
             'date_joined', 'alias', 'mobile_number'],
            ['tester', 'tester@example.com', '', '', 'False', date,
             'The Alias', '+27784667723'],
        ])

    def test_download_csv_with_an_alias_contains_ascii_code(self):
        profile = self.user.profile
        profile.alias = 'The Alias 😁'
        profile.mobile_number = '+27784667723'
        profile.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = self.user.date_joined.strftime("%Y-%m-%d %H:%M")

        self.assert_csv_download(response, 'export.csv', [
            ['username', 'email', 'first_name', 'last_name', 'is_staff',
             'date_joined', 'alias', 'mobile_number'],
            ['tester', 'tester@example.com', '', '', 'False', date,
             'The Alias 😁', '+27784667723'],
        ])

    def test_download_csv_with_an_username_contains_ascii_code(self):
        self.user.username = '사이네'
        self.user.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = self.user.date_joined.strftime("%Y-%m-%d %H:%M")

        self.assert_csv_download(response, 'export.csv', [
            ['username', 'email', 'first_name', 'last_name', 'is_staff',
             'date_joined', 'alias', 'mobile_number'],
            ['사이네', 'tester@example.com', '', '', 'False', date, '', ''],
        ])


class TestFrontendUsersAdminView(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.client.post(reverse('molo.profiles:user_register'), {
            'username': 'testing1',
            'password': '1234',
            'terms_and_conditions': True

        })
        self.user = User.objects.get(username='testing1')

        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='admin@example.com',
            password='0000',
            is_staff=True)

        self.client = Client()
        self.client.login(username='superuser', password='0000')

    def test_staff_users_are_not_shown(self):
        response = self.client.get(
            '/admin/auth/user/?usertype=frontend'
        )
        self.assertContains(response, self.user.username)
        self.assertNotContains(response, self.superuser.email)

    @override_settings(CELERY_ALWAYS_EAGER=True)
    def test_export_csv_redirects(self):
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.date_of_birth = date(1985, 1, 1)
        profile.mobile_number = '+27784667723'
        profile.save()
        response = self.client.post('/admin/auth/user/')

        self.assertEquals(response.status_code, 302)


class TestAdminUserView(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.main = Main.objects.all().first()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='0000',
            is_staff=False)

        self.superuser = User.objects.create_superuser(
            username='superuser',
            email='admin@example.com',
            password='0000',
            is_staff=True)

        self.client = Client()
        self.client.login(username='superuser', password='0000')

    def test_exclude_all_end_users(self):
        response = self.client.get(
            '/admin/auth/user/?usertype=admin'
        )
        self.assertContains(response, self.superuser.username)
        self.assertNotContains(response, self.user.username)
