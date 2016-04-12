from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.contrib.admin.sites import NotRegistered
from django.contrib import admin


try:
    admin.site.unregister(User)
except NotRegistered:
    pass


@admin.register(User)
class ProfileUserAdmin(UserAdmin):
    list_display = UserAdmin.list_display + (
        'date_joined', '_alias', '_mobile_number')

    list_filter = UserAdmin.list_filter + ('date_joined', )

    def _alias(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.alias:
            return obj.profile.alias
        return ''

    def _mobile_number(self, obj, *args, **kwargs):
        if hasattr(obj, 'profile') and obj.profile.mobile_number:
            return obj.profile.mobile_number
        return ''
