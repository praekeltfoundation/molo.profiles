from django.contrib.auth import hashers
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import ugettext_lazy as _

from molo.core.models import TranslatablePageMixin
from phonenumber_field.modelfields import PhoneNumberField
from wagtail.wagtailcore.models import Page
from wagtail.contrib.settings.models import BaseSetting, register_setting
from wagtail.wagtailadmin.edit_handlers import (
    FieldPanel, MultiFieldPanel)


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
        verbose_name=_("Mobile number required"),
    )

    prevent_phone_number_in_username = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Prevent phone number in username / display name"),
    )

    show_email_field = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Add email field to registration")
    )
    email_required = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Email required")
    )

    prevent_email_in_username = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Prevent email in username / display name"),
    )

    show_security_question_fields = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Add security question fields to registration")
    )
    security_questions_required = models.BooleanField(
        default=False,
        editable=True,
        verbose_name=_("Security questions required")
    )
    num_security_questions = models.PositiveSmallIntegerField(
        default=1,
        verbose_name=_("Number of security questions asked for "
                       "password recovery")
    )
    password_recovery_retries = models.PositiveSmallIntegerField(
        default=5,
        verbose_name=_("Max number of password recovery retries before "
                       "lockout")
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel('show_mobile_number_field'),
                FieldPanel('mobile_number_required'),
                FieldPanel('prevent_phone_number_in_username'),
            ],
            heading="Mobile Number Settings", ),
        MultiFieldPanel(
            [
                FieldPanel('show_email_field'),
                FieldPanel('email_required'),
                FieldPanel('prevent_email_in_username'),
            ],
            heading="Email Settings", ),
        MultiFieldPanel(
            [
                FieldPanel("show_security_question_fields"),
                FieldPanel("security_questions_required"),
                FieldPanel("num_security_questions"),
                FieldPanel("password_recovery_retries"),
            ],
            heading="Security Question Settings", )
    ]
    # TODO: mobile_number_required field shouldn't be shown
    # if show_mobile_number_field is False


class SecurityQuestion(TranslatablePageMixin, Page):

    class Meta:
        verbose_name = _("Security Question")

    def __str__(self):
        return self.title

SecurityQuestion.content_panels = [
    FieldPanel("title", classname="full title")
]
SecurityQuestion.promote_panels = []
SecurityQuestion.settings_panels = []


class SecurityQuestionIndexPage(Page):
    parent_page_types = []
    subpage_types = ["SecurityQuestion"]


SecurityQuestionIndexPage.content_panels = [
    FieldPanel('title', classname='full title'),
]


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
    security_question_answers = models.ManyToManyField(
        SecurityQuestion,
        through="SecurityAnswer"
    )


@receiver(post_save, sender=User)
def user_profile_handler(sender, instance, created, **kwargs):
    if created:
        profile = UserProfile(user=instance)
        profile.save()


class SecurityAnswer(models.Model):
    user = models.ForeignKey(UserProfile)
    question = models.ForeignKey(SecurityQuestion)
    answer = models.CharField(max_length=150, null=False, blank=False)

    def set_answer(self, raw_answer):
        self.answer = hashers.make_password(raw_answer.strip().lower())

    def check_answer(self, raw_answer):
        def setter(raw_answer):
            self.set_answer(raw_answer)
            self.save(update_fields=["answer"])

        return hashers.check_password(
            raw_answer.strip().lower(),
            self.answer,
            setter
        )

    def save(self, *args, **kwargs):
        if not self.id:
            self.set_answer(self.answer)
        super(SecurityAnswer, self).save(*args, **kwargs)
