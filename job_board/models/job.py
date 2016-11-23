from __future__ import unicode_literals

import tweepy

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils import timezone

from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.country import Country


class Job(models.Model):
    url = "http://daringfireball.net/projects/markdown/syntax"
    markdown = "<a href='%s'>Markdown</a>" % url
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    description = models.TextField(
                      help_text="Feel free to use %s to format "
                                "description" % markdown
                  )
    application_info = models.TextField(
                           help_text="What's the best way to apply for this "
                                     "job? %s accepted" % markdown
                       )
    location = models.CharField(
                   max_length=100,
                   blank=True,
                   null=True,
                   help_text="Specify timezone requirements or other "
                             "location-related details"
               )
    email = models.EmailField(
                help_text="This is the address we will use to contact you; "
                          "it will be not be visible on the public site"
            )
    category = models.ForeignKey(Category)
    country = models.ForeignKey(
                  Country,
                  blank=True,
                  null=True,
                  help_text="Select if you're hiring within a specific country"
              )
    company = models.ForeignKey(Company)
    paid_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    remote = models.BooleanField(
               default=False,
               help_text="Select if this job allows 100% remote working"
             )
    city = models.CharField(
               max_length=50,
               blank=True,
               null=True,
               default=None
           )
    state = models.CharField(
                max_length=50,
                blank=True,
                null=True,
                default=None)

    def activate(self):
        if self.paid_at is None:
            self.paid_at = timezone.now()
            self.save()
            self.send_tweet()
            return True
        else:
            return False

    def expire(self):
        if self.paid_at is not None and self.expired_at is None:
            sc = self.site.siteconfig_set.first()
            context = {'job': self, 'protocol': sc.protocol}
            self.expired_at = timezone.now()
            self.save()
            send_mail(
                'Your %s job has expired' % self.site.name,
                render_to_string('job_board/emails/expired.txt', context),
                sc.admin_email,
                [self.email],
                fail_silently=True,
            )
            return True
        else:
            return False

    def format_country(self):
        if self.country:
            return self.country.name
        else:
            if self.location:
                return 'Anywhere*'
            else:
                return 'Anywhere'

    def send_tweet(self):
        sc = self.site.siteconfig_set.first()
        if (not settings.DEBUG and sc.twitter_consumer_key and
                sc.twitter_consumer_secret and sc.twitter_access_token and
                sc.twitter_access_token_secret):
            auth = tweepy.OAuthHandler(
                       sc.twitter_consumer_key,
                       sc.twitter_consumer_secret
                   )
            auth.set_access_token(
                sc.twitter_access_token,
                sc.twitter_access_token_secret
            )

            api = tweepy.API(auth)

            if self.company.twitter:
                twitter = "@%s" % self.company.twitter
            else:
                twitter = self.company.name

            post = "[%s] %s at %s %s://%s/jobs/%s/" % (
                       self.format_country(),
                       self.title,
                       twitter,
                       sc.protocol,
                       self.site.domain,
                       self.id
                   )

            api.update_status(post)

    def __str__(self):
        return self.title
