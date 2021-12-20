# coding: utf-8

from django.conf import settings as user_settings

from modernrpc.conf import default_settings


class ModernRpcSettings:
    def __getattr__(self, item):

        try:
            # First, try to retrieve setting from project level settings module
            return getattr(user_settings, item)
        except AttributeError:
            # Fallback: return the default value, provided by django-modern-rpc
            return getattr(default_settings, item)


settings = ModernRpcSettings()
