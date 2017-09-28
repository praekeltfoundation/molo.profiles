from molo.profiles.admin import FrontendUsersModelAdmin, UserProfileModelAdmin
from molo.profiles.models import UserProfilesSettings, UserProfile
from wagtail.contrib.modeladmin.options import modeladmin_register
from wagtail.wagtailadmin.site_summary import SummaryItem
from wagtail.wagtailcore import hooks
from django.contrib.auth.models import User


class ProfileWarningMessagee(SummaryItem):
    order = 100
    template = 'admin/profile_warning_message.html'


@hooks.register('construct_homepage_panels')
def profile_warning_message(request, panels):
    profile_settings = UserProfilesSettings.for_site(request.site)
    if not profile_settings.country_code and \
            profile_settings.show_mobile_number_field:
        panels[:] = [ProfileWarningMessagee(request)]


modeladmin_register(FrontendUsersModelAdmin)
modeladmin_register(UserProfileModelAdmin)


class AccessErrorMessage(SummaryItem):
    order = 100
    template = 'wagtail/access_error_message.html'


@hooks.register('construct_homepage_panels')
def add_access_error_message_panel(request, panels):
    if UserProfile.objects.filter(user=request.user).exists() and \
            not request.user.is_superuser:
        if not request.user.profile.admin_sites.filter(
                pk=request.site.pk).exists():
            panels[:] = [AccessErrorMessage(request)]


@hooks.register('construct_main_menu')
def show_explorer_only_to_users_have_access(request, menu_items):
    if (request.user.is_superuser or
        (User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Moderators', 'Editors']).exists() and
         request.user.profile.admin_sites.filter(
            pk=request.site.pk).exists())):
        return menu_items
    if (User.objects.filter(pk=request.user.pk, groups__name__in=[
            'Comment Moderator', 'Expert', 'Wagtail Login Only']).exists() and
            request.user.profile.admin_sites.filter(
                pk=request.site.pk).exists()):
        menu_items[:] = [
            item for item in menu_items if item.name != 'explorer']
