from __future__ import unicode_literals

from django.dispatch import receiver
from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible


# NOTE: This uses signals to auto-create a SiteConfig object when a site is
#       added.  This saves the admin from having to manually create the site's
#       SiteConfig after a site is added.
@receiver(models.signals.post_save, sender=Site)
def generate_site_config(sender, **kwargs):
    if kwargs.get('created', True):
        site = kwargs.get('instance')
        SiteConfig.objects.get_or_create(
            site=site,
            admin_email='admin@%s' % site.domain
        )


@python_2_unicode_compatible
class SiteConfig(models.Model):
    expire_after = models.SmallIntegerField(default=30)
    # NOTE: We set a default here, but we will override this with a more
    #       suitable default when we create the SiteConfig instance
    admin_email = models.EmailField(default='admin@site')
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    def __str__(self):
        return self.site.name
