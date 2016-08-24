from django.contrib import messages
from django.contrib.auth import authenticate
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView

from molo.profiles.forms import DateOfBirthForm
from molo.profiles.forms import EditProfileForm
from molo.profiles.forms import ProfileForgotPasswordForm
from molo.profiles.forms import ProfilePasswordChangeForm
from molo.profiles.forms import RegistrationForm
from molo.profiles.models import UserProfile


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

    def get_initial(self):
        initial = super(MyProfileEdit, self).get_initial()
        initial.update({'email': self.request.user.email})
        return initial

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


class ForgotPasswordView(FormView):
    form_class = ProfileForgotPasswordForm
    template_name = 'forgot_password.html'

    # TODO: get random security question fro user's questions
    security_questions = [
        settings.SECURITY_QUESTION_1, settings.SECURITY_QUESTION_2
    ]

    def form_valid(self, form):
        if 'random_security_question_idx' not in self.request.session:
            # the session expired between the time that the form was loaded
            # and submitted, restart the process
            return HttpResponseRedirect(reverse('forgot_password'))

        if 'forgot_password_attempts' not in self.request.session:
            self.request.session['forgot_password_attempts'] = 0

        if self.request.session['forgot_password_attempts'] >= 5:
            # GEM-195 implemented a 10 min session timeout, so effectively
            # the user can only try again once their anonymous session expires.
            # If they make another request within the 10 min time window the
            # expiration will be reset to 10 mins in the future.
            # This is obviously not bulletproof as an attacker could simply
            # not send the session cookie to circumvent this.
            form.add_error(None,
                           _('Too many attempts. Please try again later.'))
            return self.render_to_response({'form': form})

        username = form.cleaned_data['username']
        random_security_question_idx = self.request.session[
            'random_security_question_idx'
        ]
        random_security_question_answer = form.cleaned_data[
            'random_security_question_answer'
        ]

        # TODO: consider moving these checks to GemForgotPasswordForm.clean()
        # see django.contrib.auth.forms.AuthenticationForm for reference
        try:
            user = User.objects.get_by_natural_key(username)
        except User.DoesNotExist:
            self.request.session['forgot_password_attempts'] += 1
            form.add_error('username',
                           _('The username that you entered appears to be '
                             'invalid. Please try again.'))
            return self.render_to_response({'form': form})

        if not user.is_active:
            form.add_error('username', 'This account is inactive.')
            return self.render_to_response({'form': form})

        is_answer_correct = False
        if random_security_question_idx == 0:
            is_answer_correct = \
                user.gem_profile.check_security_question_1_answer(
                    random_security_question_answer
                )
        elif random_security_question_idx == 1:
            is_answer_correct = \
                user.gem_profile.check_security_question_2_answer(
                    random_security_question_answer
                )
        else:
            logging.warn('Unhandled security question index')

        if not is_answer_correct:
            self.request.session['forgot_password_attempts'] += 1
            form.add_error('random_security_question_answer',
                           _('Your answer to the security question was '
                             'invalid. Please try again.'))
            return self.render_to_response({'form': form})

        token = default_token_generator.make_token(user)
        q = QueryDict(mutable=True)
        q['user'] = username
        q['token'] = token
        reset_password_url = '{0}?{1}'.format(
            reverse('reset_password'), q.urlencode()
        )

        return HttpResponseRedirect(reset_password_url)

    def render_to_response(self, context, **response_kwargs):
        random_security_question_idx = random.randint(
            0, len(self.security_questions) - 1
        )
        random_security_question = self.security_questions[
            random_security_question_idx
        ]

        context.update({
            'random_security_question': random_security_question
        })

        self.request.session['random_security_question_idx'] = \
            random_security_question_idx

        return super(GemForgotPasswordView, self).render_to_response(
            context, **response_kwargs
        )
