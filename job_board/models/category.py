from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site


class Category(models.Model):
    name = models.CharField(max_length=30)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("name", "site")
        ordering = ['name']

    def __str__(self):
        return self.name

    def active_jobs(self):
        return self.job_set.filter(paid_at__isnull=False) \
                           .filter(expired_at__isnull=True)
