from molo.profiles.forms import RegistrationForm, DateOfBirthForm
from molo.profiles.forms import EditProfileForm, ProfilePasswordChangeForm
from molo.profiles.models import UserProfile
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.core.urlresolvers import reverse, reverse_lazy
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.translation import ugettext_lazy as _


class RegistrationView(FormView):
    """
    Handles user registration
    """
    form_class = RegistrationForm
    template_name = 'profiles/register.html'

    def form_valid(self, form):
        username = form.cleaned_data['username']
        password = form.cleaned_data['password']
        mobile_number = form.cleaned_data['mobile_number']
        user = User.objects.create_user(username=username, password=password)
        user.profile.mobile_number = mobile_number
        if form.cleaned_data['email']:
            user.email = form.cleaned_data['email']
            user.save()
        user.profile.save()

        authed_user = authenticate(username=username, password=password)
        login(self.request, authed_user)
        return HttpResponseRedirect(form.cleaned_data.get('next', '/'))


class RegistrationDone(FormView):
    """
    Enables updating of the user's date of birth
    """
    form_class = DateOfBirthForm
    template_name = 'profiles/done.html'

    def form_valid(self, form):
        profile = self.request.user.profile
        profile.date_of_birth = form.cleaned_data['date_of_birth']
        profile.save()
        return HttpResponseRedirect(form.cleaned_data.get('next', '/'))


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))


class MyProfileView(TemplateView):
    """
    Enables viewing of the user's profile in the HTML site, by the profile
    owner.
    """
    template_name = 'profiles/viewprofile.html'


class MyProfileEdit(UpdateView):
    """
    Enables editing of the user's profile in the HTML site
    """
    model = UserProfile
    form_class = EditProfileForm
    template_name = 'profiles/editprofile.html'
    success_url = reverse_lazy('molo.profiles:view_my_profile')

    def form_valid(self, form):
        super(MyProfileEdit, self).form_valid(form)
        self.request.user.email = form.cleaned_data['email']
        self.request.user.save()
        return HttpResponseRedirect(
            reverse('molo.profiles:view_my_profile'))

    def get_object(self, queryset=None):
        return self.request.user.profile


class ProfilePasswordChangeView(FormView):
    form_class = ProfilePasswordChangeForm
    template_name = 'profiles/change_password.html'

    def form_valid(self, form):
        user = self.request.user
        if user.check_password(form.cleaned_data['old_password']):
            user.set_password(form.cleaned_data['new_password'])
            user.save()
            return HttpResponseRedirect(
                reverse('molo.profiles:view_my_profile'))
        messages.error(
            self.request,
            _('The old password is incorrect.')
        )
        return render(self.request, self.template_name,
                      {'form': form})
