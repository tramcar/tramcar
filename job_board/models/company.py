from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.text import slugify

from job_board.models.country import Country


class Company(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(verbose_name="URL")
    twitter = models.CharField(
                  max_length=20,
                  blank=True,
                  null=True,
                  help_text="Please leave empty if none"
              )
    country = models.ForeignKey(
                  Country,
                  blank=True,
                  null=True,
                  help_text="Please leave empty if 100% virtual",
                  on_delete=models.PROTECT
              )
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "companies"
        unique_together = ("name", "site")
        ordering = ['name']

    def __str__(self):
        return self.name

    def active_jobs(self):
        return self.job_set.filter(paid_at__isnull=False,
                                   expired_at__isnull=True)

    def paid_jobs(self):
        return self.job_set.filter(paid_at__isnull=False)

    def slug(self):
        return slugify(self.name)

    def get_absolute_url(self):
        return reverse('companies_show_slug', args=(self.id, self.slug(),))
