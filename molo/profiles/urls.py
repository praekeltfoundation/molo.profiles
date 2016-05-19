from molo.profiles import views

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required


urlpatterns = patterns(
    '',
    url(r'^logout/$', views.logout_page, name='auth_logout'),
    # If user is not login it will redirect to login page
    url(r'^login/$', 'django.contrib.auth.views.login', name='auth_login'),
    url(
        r'^register/$',
        views.RegistrationView.as_view(),
        name='user_register'),
    url(
        r'^register/done/',
        login_required(views.RegistrationDone.as_view(
            template_name="profiles/done.html"
        )),
        name='registration_done'
    ),
    url(
        r'^view/myprofile/$',
        login_required(views.MyProfileView.as_view()),
        name='view_my_profile'
    ),
    url(
        r'^edit/myprofile/$',
        login_required(views.MyProfileEdit.as_view()),
        name='edit_my_profile'
    ),
    url(
        r'^password-reset/$',
        login_required(views.ProfilePasswordChangeView.as_view()),
        name="profile_password_change"
    ),
)
