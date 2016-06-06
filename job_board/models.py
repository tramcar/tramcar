from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class Category(models.Model):
    name = models.CharField(max_length=30)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    on_site = CurrentSiteManager()

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("name", "site")

    def __str__(self):
        return self.name

    def active_jobs(self):
        return self.job_set.filter(paid_at__isnull=False).filter(expired_at__isnull=True)


@python_2_unicode_compatible
class Country(models.Model):
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        verbose_name_plural = "countries"

    def __str__(self):
        return self.name


@python_2_unicode_compatible
class Company(models.Model):
    name = models.CharField(max_length=50)
    url = models.URLField(verbose_name="URL")
    twitter = models.CharField(max_length=20)
    country = models.ForeignKey(Country, blank=True, null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    on_site = CurrentSiteManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "companies"
        unique_together = ("name", "site")

    def __str__(self):
        return self.name

    def paid_jobs(self):
        return self.job_set.filter(paid_at__isnull=False)


@python_2_unicode_compatible
class Job(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=50)
    description = models.TextField()
    application_info = models.TextField()
    location = models.TextField(blank=True)
    email = models.EmailField()
    category = models.ForeignKey(Category)
    country = models.ForeignKey(Country, blank=True, null=True)
    company = models.ForeignKey(Company)
    paid_at = models.DateTimeField(null=True)
    expired_at = models.DateTimeField(null=True)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)
    on_site = CurrentSiteManager()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def format_country(self):
        if self.country:
            return self.country.name
        else:
            if self.location:
                return 'Anywhere*'
            else:
                return 'Anywhere'

    def __str__(self):
        return self.title
