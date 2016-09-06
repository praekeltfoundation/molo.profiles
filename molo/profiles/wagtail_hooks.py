from molo.profiles.admin import (
    FrontendUsersModelAdmin, SecurityQuestionModelAdmin)
from wagtailmodeladmin.options import wagtailmodeladmin_register


wagtailmodeladmin_register(FrontendUsersModelAdmin)
wagtailmodeladmin_register(SecurityQuestionModelAdmin)
