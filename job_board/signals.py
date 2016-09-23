from __future__ import unicode_literals

from django.core.exceptions import ObjectDoesNotExist
from django.contrib.sites.models import Site

from job_board.models.site_config import SiteConfig


def gen_site_config_post_save(sender, **kwargs):
    if kwargs.get('created', True):
        site = kwargs.get('instance')
        SiteConfig.objects.get_or_create(
            site=site,
            admin_email='admin@%s' % site.domain
        )


def gen_site_config_post_migrate(plan, **kwargs):
    # A migration of the `django.contrib.sites` app was applied.
    if plan and any(migration.app_label == 'sites' for migration, _ in plan):
        try:
            site = Site.objects.get(name='example.com')
        except ObjectDoesNotExist:
            pass
        else:
            SiteConfig.objects.get_or_create(
                site=site,
                admin_email='admin@example.com',
                remote=False
            )
