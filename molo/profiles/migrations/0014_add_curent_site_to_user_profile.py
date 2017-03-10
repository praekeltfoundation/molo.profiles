# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def add_site_to_user_profile(apps, schema_editor):
    UserProfile = apps.get_model("profiles", "UserProfile")
    Main = apps.get_model("core", "Main")
    main = Main.objects.all().first()
    if main:
        site = main.get_site()
        front_end_user_profiles = UserProfile.objects.filter(
            user__is_staff=False)

        for profile in front_end_user_profiles:
            profile.site = site
            profile.save()

class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_add_site_to_profile'),
    ]

    operations = [
        migrations.RunPython(add_site_to_user_profile),
    ]
