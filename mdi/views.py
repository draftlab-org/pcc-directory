import sys

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.cache import cache
from django.shortcuts import render, reverse
from django.http import HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import api_view
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import UserSerializer, GroupSerializer, OrganizationSerializer, SectorSerializer, ToolSerializer, OrganizationIndicatorsSerializer
from .models import Organization, Sector, Tool, License
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema


def map(request):
    return HttpResponse("Where's ma maps?")


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'groups': reverse('group-list', request=request, format=format),
        'sectors': reverse('sectors-list', request=request, format=format),
        'organizations': reverse('organizations-list', request=request, format=format),
        'tools': reverse('tools-list', request=request, format=format),
    })


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Users to be viewed.
    """
    queryset = get_user_model().objects.all().order_by('date_joined')
    serializer_class = UserSerializer
    http_method_names = ['get', ]
    permission_classes = [IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Groups to be viewed.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    http_method_names = ['get', ]
    permission_classes = [IsAuthenticated]


class SectorViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Sectors to be viewed.
    """
    queryset = Sector.objects.filter(name__regex=r'^[A-Z]')
    serializer_class = SectorSerializer
    http_method_names = ['get', ]


class ToolViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Tools to be viewed.
    """
    queryset = Tool.objects.all()
    serializer_class = ToolSerializer
    http_method_names = ['get', ]


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Organizations to be viewed.
    """
    queryset = Organization.objects.all()  # filter(geom__isnull=False)
    serializer_class = OrganizationSerializer
    http_method_names = ['get', ]
    
    @swagger_auto_schema(
        responses={ status.HTTP_200_OK: OrganizationIndicatorsSerializer }
    )
    @action(detail=False, methods=['get'])
    def indicators(self, request, *args, **kwargs):
        data = { 
            'countries': len(set(self.get_queryset().exclude(country='').values_list('country', flat=True))),
            'projects': self.get_queryset().count()
        }
        serializer = OrganizationIndicatorsSerializer(data)
        return Response(serializer.data)

    def get_queryset(self):
        print('[CACHETEST] get_queryset')
        print('[CACHETEST] GETTING ORGANIZATION LIST FROM CACHE')
        queryset = cache.get('organization_queryset_all')
        if not queryset:
            print('[CACHETEST] CACHE MISS ORGANIZATION LIST')
            queryset = Organization.objects.all()
            cache.set('organization_queryset_all', queryset)
            print(f'[CACHETEST] ORGANIZATION LIST CACHED {sys.getsizeof(queryset)}')
        print(f'[CACHETEST] ORGANIZATION LIST {sys.getsizeof(queryset)}')
        return queryset

    def list(self, request, *args, **kwargs):
        print('[CACHETEST] LIST ENDPOINT')
        list_response = cache.get('organization_list')
        if not list_response:
            print('[CACHETEST] CACHE MISS LIST')
            list_response = super().list(request, *args, **kwargs)
            cache.set('organization_list', list_response)
            print(f'[CACHETEST] LIST CACHED {sys.getsizeof(list_response)}')
        print(f'[CACHETEST] LIST RESPONSE {sys.getsizeof(list_response)}')
        return list_response
