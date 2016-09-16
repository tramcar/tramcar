from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.utils.encoding import python_2_unicode_compatible


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
