from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site


class SiteConfig(models.Model):
    expire_after = models.SmallIntegerField(default=30)
    # NOTE: We set a default here, but we will override this with a more
    #       suitable default when we create the SiteConfig instance
    admin_email = models.EmailField(default='admin@site')
    site = models.OneToOneField(Site, on_delete=models.CASCADE)
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
    twitter_user = models.CharField(
                       max_length=15,
                       blank=True,
                       help_text="Your site's Twitter username, fill in to "
                                 "have a Follow icon appear on select pages"
                   )
    twitter_consumer_key = models.CharField(max_length=100, blank=True)
    twitter_consumer_secret = models.CharField(max_length=100, blank=True)
    twitter_access_token = models.CharField(max_length=100, blank=True)
    twitter_access_token_secret = models.CharField(max_length=100, blank=True)
    stripe_secret_key = models.CharField(max_length=100, blank=True)
    stripe_publishable_key = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(
                max_digits=5,
                decimal_places=2,
                default=0,
                help_text="Price to charge for posting a job, "
                          "set to 0 to disable charging"
            )
    mailchimp_username = models.CharField(max_length=20, blank=True)
    mailchimp_api_key = models.CharField(max_length=50, blank=True)
    mailchimp_list_id = models.CharField(max_length=20, blank=True)

    def price_in_cents(self):
        # Stripe expects an integer
        return int(self.price * 100)

    def __str__(self):
        return self.site.name
