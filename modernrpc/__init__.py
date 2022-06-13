# coding: utf-8
from distutils.version import StrictVersion

import django

# distutils.version, overridden by setuptools._distutils.version in recent python releases, is deprecated
# and will be removed in Python 3.12. We will probably drop Django < 3.2 until then, so this should be fine
if StrictVersion(django.get_version()) < StrictVersion("3.2"):
    # Set default_app_config only with Django up to 3.1. This prevents a Warning on newer releases
    # See https://docs.djangoproject.com/fr/3.2/releases/3.2/#automatic-appconfig-discovery
    default_app_config = "modernrpc.apps.ModernRpcConfig"

# Package version is now stored in pyproject.toml only. To retrieve it from code, use:
# import pkg_resources; version = pkg_resources.get_distribution('django-modern-rpc').version
