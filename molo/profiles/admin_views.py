from wagtailmodeladmin.views import IndexView
from wagtail.wagtailadmin import messages
from django.utils.translation import ugettext as _
from task import send_export_email
from django.shortcuts import redirect


class FrontendUsersAdminView(IndexView):
    def get_field_names(self):
        return (
            'username', 'first_name', 'last_name',
            'email', 'is_active', 'date_joined', 'last_login')

    def get_profile_field_names(self):
        return ('alias', 'date_of_birth', 'mobile_number')

    def post(self, request, *args, **kwargs):
        if not request.user.email:
            messages.error(
                request, _(
                    "Your email address is not configured. "
                    "Please update it before exporting."))
            return redirect(request.path)

        drf__date_joined__gte = request.GET.get('drf__date_joined__gte')
        drf__date_joined__lte = request.GET.get('drf__date_joined__lte')
        is_active_exact = request.GET.get('is_active__exact')

        filter_list = {
            'date_joined__range': (drf__date_joined__gte,
                                   drf__date_joined__lte) if
            drf__date_joined__gte and drf__date_joined__lte else None,
            'is_active': is_active_exact
        }

        arguments = {}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value

        field_names = self.get_field_names()
        profile_field_names = self.get_profile_field_names()
        send_export_email.delay(
            request.user.email, [field_names, profile_field_names], arguments)
        messages.success(request, _(
            "CSV emailed to '{0}'").format(request.user.email))
        return redirect(request.path)

    def get_template_names(self):
        return 'admin/frontend_users_admin_view.html'
