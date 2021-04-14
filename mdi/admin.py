from django.contrib.gis import admin
from django.contrib.gis.admin import ModelAdmin, OSMGeoAdmin, TabularInline
from accounts.models import SocialNetwork
from .models import \
    Category, Challenge, LegalStatus, Organization, OrganizationSocialNetwork, Stage, Type, Tool, License, \
    Pricing, Niche, Relationship, EntitiesEntities, Service, OrganizationAdminMember
from django.db.models.functions import Lower
from django.urls import reverse
from django.utils.safestring import mark_safe


# Window dressing
admin.site.site_header = 'Platform Coop : Map / Directory / Index'
admin.site.site_title = 'Admin'
admin.site.index_title = 'Map / Directory / Index'


# Create Admin-related classes
@admin.register(Category)
class CategoryAdmin(ModelAdmin):
    list_display = ('name', 'order', 'type', 'description')


@admin.register(Challenge)
class LegalStatusAdmin(ModelAdmin):
    list_display = ('name', 'order', 'description', )


@admin.register(LegalStatus)
class LegalStatusAdmin(ModelAdmin):
    list_display = ('name', 'order', 'description', )


@admin.register(Service)
class ServiceAdmin(ModelAdmin):
    list_display = ('name', 'order', 'description', )


@admin.register(Type)
class TypeAdmin(ModelAdmin):
    list_display = ('name', 'description', 'active')


class OrganizationSocialNetworkInline(TabularInline):
    model = OrganizationSocialNetwork
    extra = 3


@admin.register(Organization)
class OrganizationAdmin(OSMGeoAdmin):
    list_display = ('name', 'city', 'country',)
    list_filter = ('source', 'categories', 'type', 'sectors', 'country',)
    search_fields = ['name', 'description', ]
    inlines = [OrganizationSocialNetworkInline]
    ordering = [Lower('name'), ]


@admin.register(SocialNetwork)
class SocialNetworkAdmin(admin.ModelAdmin):
    list_filter = ('name', 'format', )
    search_fields = ['name', 'description', ]


@admin.register(Relationship)
class RelationshipAdmin(admin.ModelAdmin):
    list_display = ('name', )


@admin.register(EntitiesEntities)
class EntitiesEntitiesAdmin(admin.ModelAdmin):
    list_display = ('from_ind', 'from_org', 'relationship', 'to_ind', 'to_org', )


@admin.register(Stage)
class ToolAdmin(ModelAdmin):
    list_display = ('name', 'description', )


@admin.register(Niche)
class NicheAdmin(ModelAdmin):
    list_display = ('name', 'description', )


@admin.register(Tool)
class ToolAdmin(admin.ModelAdmin):
    list_display = ('name', 'license', )
    list_filter = ('niches', 'license', 'pricing')  # 'languages_supported',)
    search_fields = ['name', 'description', ]


@admin.register(License)
class LicenseAdmin(admin.ModelAdmin):
    fields = ('spdx', 'name', 'url', )
    list_display = ('spdx', 'name', 'url', )
    list_filter = ('spdx', )
    search_fields = ['spdx', 'name', ]


@admin.register(Pricing)
class PricingAdmin(admin.ModelAdmin):
    fields = ('name', )

@admin.register(OrganizationAdminMember)
class OrganizationAdminMemberAdmin(admin.ModelAdmin):
    fields = ('organization', 'member', 'approved', )
    list_display = ('organization', 'get_admin_member', 'approved', 'get_opinion_made_by', \
        'left_at', 'created_at', 'updated_at', )
    list_filter = ('approved', 'created_at', 'left_at', )
    search_fields = ('organization__name', 'organization__description', \
        'organization__email', 'member__username', 'member__first_name', \
            'member__last_name', 'member__email', )
    actions = ['make_approved', 'make_disapproved',]
    
    def get_admin_member(self, obj):
        if not obj.member:
            return None
        return mark_safe('<a href="%saccounts/user/%s/change/" target="_blank">%s</a>' % (reverse('admin:index'), obj.member.id, obj.member.get_full_name()))
    get_admin_member.short_description = 'Member Name'
    get_admin_member.empty_value_display = '-'
    get_admin_member.admin_order_field = 'member__name'
    
    def get_opinion_made_by(self, obj):
        if not obj.opinion_made_by:
            return None
        return mark_safe('<a href="%saccounts/user/%s/change/" target="_blank">%s</a>' % (reverse('admin:index'), obj.opinion_made_by.id, obj.opinion_made_by.get_full_name()))
    get_opinion_made_by.short_description = 'Opinion made by'
    get_opinion_made_by.empty_value_display = '-'
    get_opinion_made_by.admin_order_field = 'opinion_made_by'
    
    def make_approved(self, request, queryset):
        """Set request to approved."""
        user_id = request.user.pk
        for obj in queryset:
            obj.approved = True
            obj.opinion_made_by_id = user_id
            obj.save()
    make_approved.short_description = 'Approve selected request'

    def make_disapproved(self, request, queryset):
        """Set request to disapproved."""
        user_id = request.user.pk
        for obj in queryset:
            obj.approved = False
            obj.opinion_made_by_id = user_id
            obj.save()
    make_disapproved.short_description = 'Disapprove selected request'
    
    def save_model(self, request, obj, form, change):
        if getattr(obj, 'opinion_made_by', None) is None:
            obj.opinion_made_by = request.user
        obj.save()