from molo.profiles.forms import RegistrationForm
from molo.profiles.forms import EditProfileForm, ProfilePasswordChangeForm
from django.contrib.auth import logout
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _


@csrf_protect
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            user.profile.date_of_birth = form.cleaned_data['date_of_birth']
            user.profile.save()
            return HttpResponseRedirect(form.cleaned_data.get('next', '/'))
        return render(request, 'profiles/register.html', {'form': form})
    form = RegistrationForm()
    return render(request, 'profiles/register.html', {'form': form})


def logout_page(request):
    logout(request)
    return HttpResponseRedirect(request.REQUEST.get('next', '/'))


class MyProfileView(TemplateView):
    """
    Enables viewing of the user's profile in the HTML site, by the profile
    owner.
    """
    template_name = 'profiles/viewprofile.html'


class MyProfileEdit(FormView):
    """
    Enables editing of the user's profile in the HTML site
    """
    form_class = EditProfileForm
    template_name = 'profiles/editprofile.html'

    def form_valid(self, form):
        user = self.request.user
        profile = user.profile
        profile.alias = form.cleaned_data['alias']
        profile.save()
        return HttpResponseRedirect(reverse('molo.profiles:view_my_profile'))


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
