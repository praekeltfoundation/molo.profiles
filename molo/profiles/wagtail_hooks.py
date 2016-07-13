from django.contrib.auth.models import User
from django.http import HttpResponse
from molo.profiles.admin import ProfileUserAdmin
from import_export import resources
from wagtailmodeladmin.options import ModelAdmin, wagtailmodeladmin_register
from wagtailmodeladmin.views import IndexView


class FrontendUsersResource(resources.ModelResource):
    class Meta:
        model = User
        exclude = ('id', 'password', 'is_superuser', 'groups',
                   'user_permissions', 'is_staff')


class ModelAdminTemplate(IndexView):
    def post(self, request, *args, **kwargs):

        date_joined__gte = request.GET.get('date_joined__gte')
        date_joined__lt = request.GET.get('date_joined__lt')
        is_active_exact = request.GET.get('is_active_exact')

        filter_list = {
            'date_joined__range': (date_joined__gte,
                                   date_joined__lt) if
            date_joined__gte and date_joined__lt else None,
            'is_active': is_active_exact
        }

        arguments = {}

        for key, value in filter_list.items():
            if value:
                arguments[key] = value

        dataset = FrontendUsersResource().export(
            User.objects.filter(is_staff=False, **arguments))

        response = HttpResponse(dataset.csv, content_type="csv")
        response['Content-Disposition'] = \
            'attachment; filename=frontend_users.csv'
        return response

    def get_template_names(self):
        return 'admin/molo_admin_template.html'


class FrontendUsersModelAdmin(ModelAdmin, ProfileUserAdmin):
    model = User
    menu_label = 'End Users'
    menu_icon = 'user'
    menu_order = 600
    index_view_class = ModelAdminTemplate
    add_to_settings_menu = True
    list_display = ('username', '_alias', '_mobile_number',
                    'date_joined', 'is_active')

    list_filter = ('is_active', 'date_joined')

    def get_queryset(self, request):
        queryset = User.objects.filter(is_staff=False)
        return queryset

wagtailmodeladmin_register(FrontendUsersModelAdmin)
