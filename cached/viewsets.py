import logging

from django.core.cache import cache
from rest_framework import viewsets
from rest_framework.response import Response

logger = logging.getLogger(__name__)


class CachedModelViewSet(viewsets.ModelViewSet):

    def get_queryset(self):
        queryset = cache.get(f"{self.__class__.__name__}:get_queryset")
        if queryset is None:
            logger.info(f"[CACHE] Cache miss for {self.__class__.__name__}:get_queryset")
            queryset = super().get_queryset()
            cache.set(f"{self.__class__.__name__}:get_queryset", queryset)
            logger.info(f"[CACHE] Cache set for {self.__class__.__name__}:get_queryset")
        else:
            logger.info(f"[CACHE] Cache hit for {self.__class__.__name__}:get_queryset")
        return queryset

    def list(self, request, *args, **kwargs):
        print(f"[CACHE] {self.__class__.__name__}:list")
        filters = get_filters_as_string(request)
        try:
            queryset, page = cache.get(f"{self.__class__.__name__}:list:filters:{filters}")
        except:
            print(f"[CACHE] Cache miss for {self.__class__.__name__}:list:filters:{filters}")
            queryset = None
            page = None
        if queryset is None and page is None:
            logger.info(f"[CACHE] Getting data from database")
            queryset = self.filter_queryset(self.get_queryset())
            page = self.paginate_queryset(queryset)
            cache.set(f"{self.__class__.__name__}:list:filters:{filters}", (queryset, page))
        else:
            logger.info(f"[CACHE] Cache hit for {self.__class__.__name__}:list:filters:{filters}")
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        print("[CACHE] SERIALIZING")
        serializer = self.get_serializer(queryset, many=True)
        print("[CACHE] SERIALIZING DONE")
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        cache.delete(f"{self.__class__.__name__}:*")
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        cache.delete(f"{self.__class__.__name__}:*")
        return response

    def destroy(self, request, *args, **kwargs):
        response = super().destroy(request, *args, **kwargs)
        cache.delete(f"{self.__class__.__name__}:*")
        return response

    def partial_update(self, request, *args, **kwargs):
        response = super().partial_update(request, *args, **kwargs)
        cache.delete(f"{self.__class__.__name__}:*")
        return response


def get_filters_as_string(request):
    filters = request.GET
    filters_string = "&".join([f"{key}={value}" for key, value in sorted(filters.keys())])
    return filters_string