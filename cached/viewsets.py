import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets

logger = logging.getLogger(__name__)


class CachedModelViewSet(viewsets.ModelViewSet):
    CACHE_KEY_PREFIX = None

    def __init__(self, *args, **kwargs):
        if self.CACHE_KEY_PREFIX is None:
            raise ValueError("CACHE_KEY_PREFIX must be set in the viewset.")
        super().__init__(*args, **kwargs)

    @method_decorator(cache_page(60 * 15, key_prefix=CACHE_KEY_PREFIX))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        delete_cache(self.CACHE_KEY_PREFIX)
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        delete_cache(self.CACHE_KEY_PREFIX)
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        delete_cache(self.CACHE_KEY_PREFIX)
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        delete_cache(self.CACHE_KEY_PREFIX)
        return response


def delete_cache(key_prefix: str):
    """
    Delete all cache keys with the given prefix.
    """
    keys_pattern = f"views.decorators.cache.cache_*.{key_prefix}.*.{settings.LANGUAGE_CODE}.{settings.TIME_ZONE}"
    cache.delete_pattern(keys_pattern)
