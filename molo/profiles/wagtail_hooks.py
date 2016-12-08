from molo.profiles.admin import FrontendUsersModelAdmin, AdminUsersModelAdmin
from wagtailmodeladmin.options import wagtailmodeladmin_register


wagtailmodeladmin_register(FrontendUsersModelAdmin)
wagtailmodeladmin_register(AdminUsersModelAdmin)
