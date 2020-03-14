from __future__ import unicode_literals

from django.db import models
from django.contrib.sites.models import Site
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=30)
    site = models.ForeignKey(Site, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = "categories"
        unique_together = ("name", "site")
        ordering = ['name']

    def active_jobs(self):
        return self.job_set.filter(paid_at__isnull=False) \
                           .filter(expired_at__isnull=True)

    def slug(self):
        return slugify(self.name)

    def get_absolute_url(self):
        return reverse('categories_show_slug', args=(self.id, self.slug(),))

    def __str__(self):
        return self.name
