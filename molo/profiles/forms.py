from django import forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from datetime import datetime
from django.forms.extras.widgets import SelectDateWidget
from molo.profiles.models import UserProfile


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
    next = forms.CharField(required=False)

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

    class Meta:
        model = UserProfile
        fields = ['alias', 'date_of_birth']

    def clean(self):
        alias = self.cleaned_data.get('alias', None)
        date_of_birth = self.cleaned_data.get('date_of_birth', None)
        if (alias or date_of_birth):
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
