from import_export import resources
from django.contrib.auth.models import User


class FrontendUsersResource(resources.ModelResource):
    class Meta:
        model = User
        exclude = ('id', 'password', 'is_superuser', 'groups',
                   'user_permissions', 'is_staff')
