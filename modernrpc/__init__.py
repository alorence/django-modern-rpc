# coding: utf-8

# default_app_config was deprecated in Django 3.2. Maybe set it only when detected django version is older?
default_app_config = "modernrpc.apps.ModernRpcConfig"

# Package version is now stored in pyproject.toml only. To retrieve it from code, use:
# import pkg_resources; version = pkg_resources.get_distribution('django-modern-rpc').version
