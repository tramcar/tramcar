from __future__ import unicode_literals

import tweepy

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify

from utils.misc import send_mail_with_helper

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
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    country = models.ForeignKey(
                  Country,
                  blank=True,
                  null=True,
                  help_text="Select if you're hiring within a specific "
                            "country",
                  on_delete=models.PROTECT
              )
    company = models.ForeignKey(Company, on_delete=models.PROTECT)
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
            context = {'job': self, 'protocol': self.site.siteconfig.protocol}
            self.expired_at = timezone.now()
            self.save()
            send_mail_with_helper(
                'Your %s job has expired' % self.site.name,
                render_to_string('job_board/emails/expired.txt', context),
                self.site.siteconfig.admin_email,
                [self.email]
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
        sc = self.site.siteconfig
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

    def slug(self):
        return slugify('%s-%s' % (self.title, self.company.name))

    def get_absolute_url(self):
        return reverse('jobs_show_slug', args=(self.id, self.slug(),))

    def __str__(self):
        return self.title
