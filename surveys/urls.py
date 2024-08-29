from django.urls import path
from . views import index, ECOSYSTEM_FORMS, EcosystemWizard
from mdi.models import OrganizationSocialNetwork

urlpatterns = [
    path(r'^$', index),
    path(r'ecosystem-2020/',
         EcosystemWizard.as_view(ECOSYSTEM_FORMS, instance_dict={'social_networks': OrganizationSocialNetwork}),
         name='ecosystem-2020'),
]
