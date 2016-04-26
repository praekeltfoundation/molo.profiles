import csv

from django.contrib import admin
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered

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
        obj.date_joined = obj.date_joined.strftime("%Y-%m-%d %H:%M")
        writer.writerow(
            [getattr(obj, field) for field in user_model_fields] +
            [getattr(obj.profile, field) for field in profile_fields])
    return response
download_as_csv.short_description = "Download selected as csv"


@admin.register(User)
class ProfileUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'date_joined', '_alias', '_mobile_number')

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
