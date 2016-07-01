# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-06-30 12:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0003_add_email_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofilessettings',
            name='prevent_email_in_username',
            field=models.BooleanField(default=False, verbose_name='Prevent email in username / display name'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='prevent_number_in_username',
            field=models.BooleanField(default=False, verbose_name='Prevent number in username / display name'),
        ),
    ]
