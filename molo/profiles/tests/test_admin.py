# -*- coding: utf-8 -*-
from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.test.client import Client
from datetime import date
from molo.core.tests.base import MoloTestCaseMixin

from molo.profiles.admin import ProfileUserAdmin, download_as_csv
from molo.profiles.models import UserProfile


class ModelsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.mk_main()

    def test_download_csv(self):
        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.mobile_number = '+27784667723'
        profile.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = str(self.user.date_joined.strftime("%Y-%m-%d %H:%M"))
        expected_output = ('Content-Type: text/csv\r\nContent-Disposition: '
                           'attachment;filename=export.csv\r\n\r\nusername,'
                           'email,first_name,last_name,is_staff,date_joined,'
                           'alias,mobile_number\r\ntester,tester@example.com,'
                           ',,False,' + date + ',The Alias,+27784667723\r\n')
        self.assertEquals(str(response), expected_output)

    def test_download_csv_with_an_alias_contains_ascii_code(self):
        profile = self.user.profile
        profile.alias = 'The Alias 😁'
        profile.mobile_number = '+27784667723'
        profile.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = str(self.user.date_joined.strftime("%Y-%m-%d %H:%M"))
        expected_output = ('Content-Type: text/csv\r\nContent-Disposition: '
                           'attachment;filename=export.csv\r\n\r\nusername,'
                           'email,first_name,last_name,is_staff,date_joined,'
                           'alias,mobile_number\r\ntester,tester@example.com,'
                           ',,False,' + date + ',The Alias \xf0\x9f\x98\x81,'
                           '+27784667723\r\n')
        self.assertEquals(str(response), expected_output)

    def test_download_csv_with_an_username_contains_ascii_code(self):
        self.user.username = '사이네'
        self.user.save()

        response = download_as_csv(ProfileUserAdmin(UserProfile, self.site),
                                   None,
                                   User.objects.all())
        date = str(self.user.date_joined.strftime("%Y-%m-%d %H:%M"))
        expected_output = ('Content-Type: text/csv\r\nContent-Disposition: '
                           'attachment;filename=export.csv\r\n\r\nusername,'
                           'email,first_name,last_name,is_staff,date_joined,'
                           'alias,mobile_number\r\n\xec\x82\xac\xec\x9d\xb4'
                           '\xeb\x84\xa4,tester@example.com,'
                           ',,False,' + date + ',,\r\n')
        self.assertEquals(str(response), expected_output)


class TestFrontendUsersAdminView(TestCase):
    def setUp(self):
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


class TestAdminUserView(TestCase):
    def setUp(self):
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
