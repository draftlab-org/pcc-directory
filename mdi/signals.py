from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site
from mdi.models import OrganizationAdminMember
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model


def send_mail(template, subject, to, context):
    content = render_to_string(template, context)
    to_list = to if isinstance(to, list) else [to]
    from_email = settings.DEFAULT_FROM_EMAIL
    text_content = content
    msg = EmailMultiAlternatives(subject, text_content, from_email, to_list)
    msg.send()


@receiver(pre_save, sender=OrganizationAdminMember)
def send_org_admin_member_request(sender, instance, **kwargs):
    if not instance.id:
        org = instance.organization
        member = instance.member
        # Member notify
        member_emaiL_template = 'email/organization_admin_member_request.txt'
        member_subject = _('Your request has been sent successfully')
        context = {
            'member': member,
            'organization': org
        }
        send_mail(member_emaiL_template, member_subject, member.email, context)
        # Admin notify
        domain = Site.objects.first().domain
        organization_url = '%s%s' % (domain, reverse('organization-detail', kwargs={'organization_id': org.pk}))
        admin_emaiL_template = 'email/organization_admin_member_request_admin.txt'
        admin_subject = _('Your request has been sent successfully')
        admin_targets = set(org.organization_admins_members.filter(approved=True, left_at__isnull=True).values_list('member__email', flat=True))
        admin_targets.union(set(get_user_model().objects.filter(is_superuser=True, is_active=True).values_list('email', flat=True)))
        if org.admin_email:
            admin_targets.add(org.admin_email)
       
        context.update({
            'organization_url': organization_url,
        })
        send_mail(admin_emaiL_template, admin_subject, list(admin_targets), context)
        
    
    db_instance = OrganizationAdminMember.objects.filter(pk=instance.pk).first()
    if db_instance and db_instance.approved != instance.approved and instance.approved:
        domain = Site.objects.first().domain
        emaiL_template = 'email/organization_admin_member_request_approved.txt'
        subject = _('Your request has been approved')
        profile_url = '%s%s' % (domain, reverse('my-profiles'))
        organization_url = '%s%s' % (domain, reverse('organization-detail', kwargs={'organization_id': instance.organization.pk}))
        context = {
            'member': instance.member,
            'organization': instance.organization,
            'profile_url': profile_url,
            'organization_url': organization_url,
        }
        send_mail(emaiL_template, subject, instance.member.email, context)
    
    if db_instance and db_instance.approved != instance.approved and instance.approved is not None and not instance.approved:
        emaiL_template = 'email/organization_admin_member_request_reproved.txt'
        subject = _('Your request has been reproved')
        context = {
            'member': instance.member,
            'organization': instance.organization
        }
        send_mail(emaiL_template, subject, instance.member.email, context)
