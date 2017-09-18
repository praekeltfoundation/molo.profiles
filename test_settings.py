from .base import INSTALLED_APPS, AUTHENTICATION_BACKENDS

INSTALLED_APPS = INSTALLED_APPS + [
    'import_export',
]

AUTHENTICATION_BACKENDS = [
    'molo.profiles.backends.MoloProfilesModelBackend', ] + \
    AUTHENTICATION_BACKENDS
