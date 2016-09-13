from __future__ import unicode_literals

from django.dispatch import receiver
from django.db import models
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.encoding import python_2_unicode_compatible


# NOTE: This uses signals to auto-create a SiteConfig object when a site is
#       added.  This saves the admin from having to manually create the site's
#       SiteConfig after a site is added.
@receiver(models.signals.post_save, sender=Site)
def gen_site_config_post_save(sender, **kwargs):
    if kwargs.get('created', True):
        site = kwargs.get('instance')
        SiteConfig.objects.get_or_create(
            site=site,
            admin_email='admin@%s' % site.domain
        )


# NOTE: The above (gen_site_config) used to work for the initial site created
#       by the sites framework, however with the Django 1.10 upgrade this no
#       worked.  This separate handler is to ensure that the initial
#       example.com site gets a SiteConfig entry created also.
@receiver(models.signals.post_migrate)
def gen_site_config_post_migrate(plan, **kwargs):
    # A migration of the `django.contrib.sites` app was applied.
    if plan and any(migration.app_label == 'sites' for migration, _ in plan):
        try:
            site = Site.objects.get(name='example.com')
        except ObjectDoesNotExist:
            pass
        else:
            SiteConfig.objects.get_or_create(
                site=site,
                admin_email='admin@example.com',
                remote=False
            )


@python_2_unicode_compatible
class SiteConfig(models.Model):
    expire_after = models.SmallIntegerField(default=30)
    # NOTE: We set a default here, but we will override this with a more
    #       suitable default when we create the SiteConfig instance
    admin_email = models.EmailField(default='admin@site')
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    remote = models.BooleanField(
               default=False,
               help_text="Select if this job board is for remote jobs only")

    def __str__(self):
        return self.site.name
