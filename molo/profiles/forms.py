from datetime import datetime

from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from wagtail.wagtailcore.models import Site
from wagtail.contrib.settings.context_processors import SettingsProxy

from molo.profiles.models import UserProfile

from phonenumber_field.formfields import PhoneNumberField


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

    def clean_username(self):
        if User.objects.filter(
            username__iexact=self.cleaned_data['username']
        ).exists():
            raise forms.ValidationError(_("Username already exists."))
        return self.cleaned_data['username']


class DateOfBirthForm(forms.Form):
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed([y for y in range(1930, datetime.now().year)]))
        )
    )


class EditProfileForm(forms.ModelForm):
    alias = forms.CharField(
        label=_("Display Name"),
        required=False
    )
    date_of_birth = forms.DateField(
        widget=SelectDateWidget(
            years=list(reversed([y for y in range(1930, datetime.now().year)]))
        ),
        required=False
    )
    mobile_number = PhoneNumberField(required=False)
    email = forms.EmailField(required=False)

    class Meta:
        model = UserProfile
        fields = ['alias', 'date_of_birth', 'mobile_number']

    def clean(self):
        alias = self.cleaned_data.get('alias', None)
        date_of_birth = self.cleaned_data.get('date_of_birth', None)
        mobile_number = self.cleaned_data.get('mobile_number', None)
        email = self.cleaned_data.get('email', None)
        if (alias or date_of_birth or mobile_number or email):
            return self.cleaned_data
        else:
            raise forms.ValidationError(_('Please enter a new value.'))


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
