from django.utils import timezone

import re

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

from molo.profiles.models import UserProfile

from phonenumber_field.formfields import PhoneNumberField


REGEX_PHONE = settings.REGEX_PHONE if hasattr(settings, 'REGEX_PHONE') else \
    r'.*?(\(?\d{3})? ?[\.-]? ?\d{3} ?[\.-]? ?\d{4}.*?'

REGEX_EMAIL = settings.REGEX_EMAIL if hasattr(settings, 'REGEX_PHONE') else \
    r'([\w\.-]+@[\w\.-]+)'


def get_validation_msg_fragment():
    site = Site.objects.get(is_default_site=True)
    settings = SettingsProxy(site)
    profile_settings = settings['profiles']['UserProfilesSettings']

    invalid_msg = ''

    if getattr(profile_settings, 'prevent_email_in_username', False) \
            and getattr(profile_settings, 'prevent_phone_number_in_username',
                        False):
        invalid_msg = 'phone number or email address'

    elif getattr(profile_settings, 'prevent_phone_number_in_username', False):
        invalid_msg = 'phone number'

    elif getattr(profile_settings, 'prevent_email_in_username', False):
        invalid_msg = 'email address'

    return invalid_msg


def validate_no_email_or_phone(input):
    site = Site.objects.get(is_default_site=True)
    settings = SettingsProxy(site)
    profile_settings = settings['profiles']['UserProfilesSettings']

    regexes = []
    if profile_settings.prevent_phone_number_in_username:
        regexes.append(REGEX_PHONE)

    if profile_settings.prevent_email_in_username:
        regexes.append(REGEX_EMAIL)

    for regex in regexes:
        match = re.search(regex, input)
        if match:
            return False

    return True


class RegistrationForm(forms.Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )
    password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("PIN")
    )
    email = forms.EmailField(required=False)
    mobile_number = PhoneNumberField(required=False)
    terms_and_conditions = forms.BooleanField(required=True)
    next = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super(RegistrationForm, self).__init__(*args, **kwargs)
        site = Site.objects.get(is_default_site=True)
        settings = SettingsProxy(site)
        profile_settings = settings['profiles']['UserProfilesSettings']
        self.fields['mobile_number'].required = (
            profile_settings.mobile_number_required and
            profile_settings.show_mobile_number_field)
        self.fields['email'].required = (
            profile_settings.email_required and
            profile_settings.show_email_field)

        # Security questions fields are created dynamically.
        # This allows any number of security questions to be specified
        for index, question in enumerate(questions):
            self.fields["question_%s" % index] = forms.CharField(
                label=_(str(question)),
                widget=forms.TextInput(
                    attrs=dict(
                        max_length=150,
                    )
                )
            )
            self.fields["question_%s" % index].required = (
                profile_settings.show_security_question_fields and
                profile_settings.security_questions_required
            )

    def security_questions(self):
        return [
            self[name] for name in filter(
                lambda x: x.startswith('question_'), self.fields.keys()
            )
        ]

    def clean_username(self):
        validation_msg_fragment = get_validation_msg_fragment()

        if User.objects.filter(
                username__iexact=self.cleaned_data['username']
        ).exists():
            raise forms.ValidationError(_("Username already exists."))

        if not validate_no_email_or_phone(self.cleaned_data['username']):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid username. Please don't use"
                    " your %s in your username." % validation_msg_fragment
                )
            )

        return self.cleaned_data['username']


class DateOfBirthForm(forms.Form):
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed(range(1930, timezone.now().year + 1)))
        )
    )


class EditProfileForm(forms.ModelForm):
    alias = forms.CharField(
        label=_("Display Name"),
        required=False
    )
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed(range(1930, timezone.now().year + 1)))
        ),
        required=False
    )
    mobile_number = PhoneNumberField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ['alias', 'date_of_birth', 'mobile_number']

    def clean_alias(self):
        validation_msg_fragment = get_validation_msg_fragment()

        alias = self.cleaned_data['alias']

        if not validate_no_email_or_phone(alias):
            raise forms.ValidationError(
                _(
                    "Sorry, but that is an invalid display name. "
                    "Please don't use your %s in your display name."
                    % validation_msg_fragment
                )
            )

        return alias


class ProfilePasswordChangeForm(forms.Form):
    old_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4, min_length=4,
        error_messages={'invalid': _("This value must contain only  \
         numbers.")},
        label=_("Old Password")
    )
    new_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={'invalid': _("This value must contain only  \
         numbers.")},
        label=_("New Password")
    )
    confirm_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("Confirm Password")
    )

    def clean(self):
        new_password = self.cleaned_data.get('new_password', None)
        confirm_password = self.cleaned_data.get('confirm_password', None)
        if (new_password and confirm_password and
                (new_password == confirm_password)):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_('New passwords do not match.'))


class ForgotPasswordForm(forms.Form):
    username = forms.RegexField(
        regex=r'^[\w.@+-]+$',
        widget=forms.TextInput(
            attrs=dict(
                required=True,
                max_length=30,
            )
        ),
        label=_("Username"),
        error_messages={
            'invalid': _("This value must contain only letters, "
                         "numbers and underscores."),
        }
    )

    def __init__(self, *args, **kwargs):
        questions = kwargs.pop("questions")
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

        for index, question in enumerate(questions):
            self.fields["question_%s" % index] = forms.CharField(
                label=_(str(question)),
                widget=forms.TextInput(
                    attrs=dict(
                        required=True,
                        max_length=150,
                    )
                )
            )


class ResetPasswordForm(forms.Form):
    username = forms.CharField(
        widget=forms.HiddenInput()
    )

    token = forms.CharField(
        widget=forms.HiddenInput()
    )

    password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("PIN")
    )

    confirm_password = forms.RegexField(
        regex=r'^\d{4}$',
        widget=forms.PasswordInput(
            attrs=dict(
                required=True,
                render_value=False,
                type='password',
            )
        ),
        max_length=4,
        min_length=4,
        error_messages={
            'invalid': _("This value must contain only numbers."),
        },
        label=_("Confirm PIN")
    )
