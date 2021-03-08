from django.core.cache import cache


def ensure_sequence(element):
    """Ensure the given argument is a sequence object (tuple, list). If not, return a list containing its value."""
    return element if isinstance(element, (tuple, list)) else [element]


def clean_old_cache_content():
    """Clean CACHE data from old versions of django-modern-rpc"""
    cache.delete('__rpc_registry__', version=1)
