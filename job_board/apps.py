from __future__ import unicode_literals

from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.models.signals import post_save


class JobBoardConfig(AppConfig):
    name = 'job_board'

    def ready(self):
        from django.contrib.sites.models import Site

        from job_board.signals import gen_site_config_post_migrate
        from job_board.signals import gen_site_config_post_save

        post_save.connect(gen_site_config_post_save, sender=Site)
        # NOTE: We list sites before job_board in INSTALLED_APPS, failing to
        #       do that will result in this post_migrate signal firing before
        #       the default site has been created.
        post_migrate.connect(gen_site_config_post_migrate, sender=self)
