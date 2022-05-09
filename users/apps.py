import os

from django.apps import AppConfig
from django.conf import settings


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        if not os.path.isdir(settings.MEDIA_ROOT):
            os.mkdir(settings.MEDIA_ROOT)