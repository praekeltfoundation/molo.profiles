# -*- coding: utf-8 -*-
from django.core import mail
from django.test import TestCase
from django.contrib.auth.models import User
from django.conf import settings
from molo.core.tests.base import MoloTestCaseMixin
from molo.profiles.task import send_export_email


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

    def test_send_export_email(self):
        send_export_email(self.user.email, {})
        message = list(mail.outbox)[0]
        self.assertEquals(message.to, [self.user.email])
        self.assertEquals(
            message.subject, 'Molo export: ' + settings.SITE_NAME)
        self.assertEquals(
            message.attachments[0],
            ('Molo_export_testapp.csv',
             'username,alias,first_name,last_name,date_of_birth,email,mobile_n'
             'umber,is_active,date_joined,last_login\r\ntester,The Alias,,,,'
             'tester@example.com,+27784667723,1,' + str(
                 self.user.date_joined.strftime("%Y-%m-%d %H:%M:%S")) +
             ',\r\n',
             'text/csv'))
