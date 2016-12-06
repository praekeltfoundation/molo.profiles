# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.task import get_front_end_user_csv_file, send_export_email


class ModelsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.user = User.objects.create_user(
            username='tester',
            email='tester@example.com',
            password='tester')
        self.mk_main()

        profile = self.user.profile
        profile.alias = 'The Alias'
        profile.mobile_number = '+27784667723'
        profile.save()
        self.field_names = (
            'username', 'first_name', 'last_name',
            'email', 'is_active', 'date_joined', 'last_login')
        self.profile_field_names = (
            'alias', 'date_of_birth', 'mobile_number'
        )

    def test_front_end_user_csv_output(self):
        csv_file = get_front_end_user_csv_file([
            self.field_names, self.profile_field_names], {})
        self.assertEquals(
            csv_file.getvalue(),
            'username,first_name,last_name,email,is_active,date_joined,last_lo'
            'gin,alias,date_of_birth,mobile_number\r\ntester,,,tester@example'
            '.com,True,' + str(self.user.date_joined.strftime(
                "%Y-%m-%d %H:%M")) + ',,The Alias,,+27784667723\r\n')

    def test_front_end_user_csv_output_ascii_code(self):
        profile = self.user.profile
        profile.alias = 'The Alias 😁'
        profile.mobile_number = '+27784667723'
        profile.save()
        csv_file = get_front_end_user_csv_file([
            self.field_names, self.profile_field_names], {})
        self.assertEquals(
            csv_file.getvalue(),
            'username,first_name,last_name,email,is_active,date_joined,'
            'last_login,alias,date_of_birth,mobile_number\r\ntester,,,tester@'
            'example.com,True,' + str(self.user.date_joined.strftime(
                "%Y-%m-%d %H:%M")) + ',,The Alias \xf0\x9f\x98\x81,,+2'
            '7784667723\r\n')

    def test_send_export_email(self):
        send_export_email(self.user.email, [
            self.field_names, self.profile_field_names], {})
        message = list(mail.outbox)[0]
        self.assertEquals(message.to, [self.user.email])
        self.assertEquals(
            message.subject, 'Molo export: ' + settings.SITE_NAME)
        self.assertEquals(
            message.attachments[0],
            ('Molo_export_testapp.csv',
             'username,first_name,last_name,email,is_active,date_joined,last_l'
             'ogin,alias,date_of_birth,mobile_number\r\ntester,,,tester@exampl'
             'e.com,True,' + str(self.user.date_joined.strftime(
                 "%Y-%m-%d %H:%M")) + ',,The Alias,,+277846677'
             '23\r\n', 'text/csv'))
