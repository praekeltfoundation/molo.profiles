from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.contrib.settings.models import BaseSetting, register_setting
from django.utils.translation import ugettext_lazy as _


@register_setting
class UserProfilesSettings(BaseSetting):
    show_mobile_number_field = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Add mobile number field to registration"),
    )
    mobile_number_required = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_('Mobile number required'),
    )
    # TODO: mobile_number_required field shouldn't be shown
    # if show_mobile_number_field is False


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name="profile", primary_key=True)
    date_of_birth = models.DateField(null=True)
    alias = models.CharField(
        max_length=128,
        blank=True,
        null=True)
    avatar = models.ImageField(
        'avatar',
        max_length=100,
        upload_to='users/profile',
        blank=True,
        null=True)

    mobile_number = PhoneNumberField(blank=True, null=True, unique=False)


@receiver(post_save, sender=User)
def user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()
