import csv

from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered

from daterange_filter.filter import DateRangeFilter
from wagtailmodeladmin.options import ModelAdmin as WagtailModelAdmin

from molo.profiles.admin_views import FrontendUsersAdminView

try:
    admin.site.unregister(User)
except NotRegistered:
    pass


def download_as_csv(ProfileUserAdmin, request, queryset):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment;filename=export.csv'
    writer = csv.writer(response)
    user_model_fields = UserAdmin.list_display + ('date_joined', )
    profile_fields = ('alias', 'mobile_number')
    field_names = user_model_fields + profile_fields
    writer.writerow(field_names)
    for obj in queryset:
        if obj.profile.alias:
            obj.profile.alias = obj.profile.alias.encode('utf-8')
        obj.username = obj.username.encode('utf-8')
        obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
        writer.writerow(
            [getattr(obj, field) for field in user_model_fields] +
            [getattr(obj.profile, field) for field in profile_fields])
    return response
download_as_csv.short_description = "Download selected as csv"


@admin.register(User)
class ProfileUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'date_joined', '_alias', '_mobile_number', '_date_of_birth')

    list_filter = UserAdmin.list_filter + ('date_joined', )

    actions = [download_as_csv]

    def _alias(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.alias:
            return obj.profile.alias
        return ''

    def _mobile_number(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.mobile_number:
            return obj.profile.mobile_number
        return ''

    def _date_of_birth(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.date_of_birth:
            return obj.profile.date_of_birth
        return ''


# Below here is for Wagtail Admin
class FrontendUsersDateRangeFilter(DateRangeFilter):
    template = 'admin/frontend_users_date_range_filter.html'


class FrontendUsersModelAdmin(WagtailModelAdmin, ProfileUserAdmin):
    model = User
    menu_label = 'End Users'
    menu_icon = 'user'
    menu_order = 600
    index_view_class = FrontendUsersAdminView
    add_to_settings_menu = True
    list_display = ('username', '_alias', '_mobile_number', '_date_of_birth',
                    'email', 'date_joined', 'is_active')

    list_filter = (('date_joined', FrontendUsersDateRangeFilter), 'is_active')

    search_fields = ('username',)

    def get_queryset(self, request):
        queryset = User.objects.filter(is_staff=False)
        return queryset
