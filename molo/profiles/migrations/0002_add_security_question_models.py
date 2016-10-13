# -*- coding: utf-8 -*-
# Generated by Django 1.9.9 on 2016-10-12 17:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import molo.core.models
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '0028_merge'),
        ('profiles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SecurityAnswer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answer', models.CharField(max_length=150)),
            ],
        ),
        migrations.CreateModel(
            name='SecurityQuestion',
            fields=[
                ('page_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='wagtailcore.Page')),
            ],
            options={
                'verbose_name': 'Security Question',
            },
            bases=(molo.core.models.TranslatablePageMixin, 'wagtailcore.page'),
        ),
        migrations.CreateModel(
            name='UserProfilesSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('show_mobile_number_field', models.BooleanField(default=False, verbose_name='Add mobile number field to registration')),
                ('mobile_number_required', models.BooleanField(default=False, verbose_name='Mobile number required')),
                ('prevent_phone_number_in_username', models.BooleanField(default=False, verbose_name='Prevent phone number in username / display name')),
                ('show_email_field', models.BooleanField(default=False, verbose_name='Add email field to registration')),
                ('email_required', models.BooleanField(default=False, verbose_name='Email required')),
                ('prevent_email_in_username', models.BooleanField(default=False, verbose_name='Prevent email in username / display name')),
                ('show_security_question_fields', models.BooleanField(default=False, verbose_name='Add security question fields to registration')),
                ('security_questions_required', models.BooleanField(default=False, verbose_name='Security questions required')),
                ('num_security_questions', models.PositiveSmallIntegerField(default=1, verbose_name='Number of security questions asked for password recovery')),
                ('password_recovery_retries', models.PositiveSmallIntegerField(default=5, verbose_name='Max number of password recovery retries before lockout')),
                ('site', models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, to='wagtailcore.Site')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='userprofile',
            name='mobile_number',
            field=phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='securityanswer',
            name='question',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.SecurityQuestion'),
        ),
        migrations.AddField(
            model_name='securityanswer',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='profiles.UserProfile'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='security_question_answers',
            field=models.ManyToManyField(through='profiles.SecurityAnswer', to='profiles.SecurityQuestion'),
        ),
    ]
