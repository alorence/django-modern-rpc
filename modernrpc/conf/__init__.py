from django.conf import settings as user_settings

from modernrpc.conf import default_settings


class ModernRpcSettings:

    def __getattr__(self, item):
        return getattr(user_settings, item, getattr(default_settings, item))


settings = ModernRpcSettings()
