# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-03-20 14:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0014_add_curent_site_to_user_profile'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='education_level',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='location',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='activate_display_name',
            field=models.BooleanField(default=False, verbose_name='Activate Display Name'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='activate_dob',
            field=models.BooleanField(default=False, verbose_name='Activate Date Of Birth'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='activate_education_level',
            field=models.BooleanField(default=False, verbose_name='Activate Education Level'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='activate_education_level_required',
            field=models.BooleanField(default=False, verbose_name='Education Level Required'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='activate_gender',
            field=models.BooleanField(default=False, verbose_name='Activate Gender'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='activate_location',
            field=models.BooleanField(default=False, verbose_name='Activate Location'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='capture_display_name',
            field=models.BooleanField(default=False, verbose_name='Capture Display Name'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='capture_dob',
            field=models.BooleanField(default=False, verbose_name='Capture Date Of Birth'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='capture_education_level',
            field=models.BooleanField(default=False, verbose_name='Capture Education Level'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='capture_gender',
            field=models.BooleanField(default=False, verbose_name='Capture Gender'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='capture_location',
            field=models.BooleanField(default=False, verbose_name='Capture Location'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='display_name_required',
            field=models.BooleanField(default=False, verbose_name='Display Name Required'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='dob_required',
            field=models.BooleanField(default=False, verbose_name='Date Of Birth Required'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='gender_required',
            field=models.BooleanField(default=False, verbose_name='Gender Required'),
        ),
        migrations.AddField(
            model_name='userprofilessettings',
            name='location_required',
            field=models.BooleanField(default=False, verbose_name='Location Required'),
        ),
    ]
