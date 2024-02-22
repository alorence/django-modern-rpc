import django

if django.VERSION < (3, 2):
    # Set default_app_config only with Django up to 3.1. This prevents a Warning on newer releases
    # See https://docs.djangoproject.com/fr/3.2/releases/3.2/#automatic-appconfig-discovery
    default_app_config = "modernrpc.apps.ModernRpcConfig"

# Package version is now stored only in pyproject.toml. To retrieve it from code, use:
#   import pkg_resources; version = pkg_resources.get_distribution('django-modern-rpc').version
# or in recent Python version (> 3.11), use
#   import importlib.metadata; version = importlib.metadata.version("django-modern-rpc")
