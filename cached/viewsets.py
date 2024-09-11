import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
# from rest_framework.response import Response

logger = logging.getLogger(__name__)


class CachedModelViewSet(viewsets.ModelViewSet):
    CACHE_KEY_PREFIX = None

    def __init__(self):
        if self.CACHE_KEY_PREFIX is None:
            raise ValueError("CACHE_KEY_PREFIX must be set in the viewset.")
        super().__init__()

    # def get_queryset(self):
    #     queryset = cache.get(f"{self.__class__.__name__}:get_queryset")
    #     if queryset is None:
    #         logger.info(f"[CACHE] Cache miss for {self.__class__.__name__}:get_queryset")
    #         queryset = super().get_queryset()
    #         cache.set(f"{self.__class__.__name__}:get_queryset", queryset)
    #         logger.info(f"[CACHE] Cache set for {self.__class__.__name__}:get_queryset")
    #     else:
    #         logger.info(f"[CACHE] Cache hit for {self.__class__.__name__}:get_queryset")
    #     return queryset
    #
    # def list(self, request, *args, **kwargs):
    #     queryset, page = cache.get(f"{self.__class__.__name__}:list")
    #     if queryset is None and page is None:
    #         logger.info(f"[CACHE] Cache miss for {self.__class__.__name__}:list")
    #         queryset = self.filter_queryset(self.get_queryset())
    #         page = self.paginate_queryset(queryset)
    #         cache.set(f"{self.__class__.__name__}:list", (queryset, page))
    #     else:
    #         logger.info(f"[CACHE] Cache hit for {self.__class__.__name__}:list")
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(queryset, many=True)
    #     return Response(serializer.data)

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
