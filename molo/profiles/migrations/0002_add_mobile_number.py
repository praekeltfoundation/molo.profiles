# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0023_alter_page_revision_on_delete_behaviour'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfilesSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('show_mobile_number_filed', models.BooleanField(default=True, verbose_name="Ask user's mobile number")),
                ('mobile_number_required', models.BooleanField(default=True, verbose_name='Mobile number required')),
                ('site', models.OneToOneField(editable=False, to='wagtailcore.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mobile_number',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, unique=True, null=True, blank=True),
        ),
    ]
