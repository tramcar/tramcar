from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site


class SiteConfig(models.Model):
    expire_after = models.SmallIntegerField(default=30)
    # NOTE: We set a default here, but we will override this with a more
    #       suitable default when we create the SiteConfig instance
    admin_email = models.EmailField(default='admin@site')
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    remote = models.BooleanField(
                 default=False,
                 help_text="Select if this job board is for remote jobs only"
             )
    protocol = models.CharField(
                   default='http',
                   choices=(('http', 'http'), ('https', 'https')),
                   max_length=5,
                   help_text="The protocol to use when building links in "
                             "e-mail templates, etc."
               )
    google_analytics = models.CharField(
                           max_length=20,
                           blank=True,
                           help_text="Google Analytics Tracking ID"
                       )
    twitter = models.CharField(
                  max_length=15,
                  blank=True
              )

    def __str__(self):
        return self.site.name
