# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_site_to_user_profile(apps, schema_editor):
    UserProfile = apps.get_model("profiles", "UserProfile")
    Site = apps.get_model("wagtailcore", "Site")
    site = Site.objects.all().first()
    if site:
        UserProfile.objects.filter(user__is_staff=False).update(site=site)

class Migration(migrations.Migration):

    dependencies = [
        ('wagtailcore', '__latest__'),
        ('profiles', '0013_add_site_to_profile'),
    ]

    operations = [
        migrations.RunPython(add_site_to_user_profile),
    ]
