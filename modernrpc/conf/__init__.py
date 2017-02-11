from django.conf import settings as project_settings

from modernrpc.conf import default_settings


class ModernRpcSettings:

    def __getattr__(self, item):
        return getattr(project_settings, item, getattr(default_settings, item))


settings = ModernRpcSettings()
