from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from job_board.models import Job, Site


class Command(BaseCommand):
    help = 'Expire all jobs older than 30 days'

    def handle(self, *args, **options):
        for site in Site.objects.all():
            sc = site.siteconfig_set.first()
            days_ago = timezone.now() - timedelta(days=sc.expire_after)
            jobs = Job.objects.filter(site=site) \
                              .filter(paid_at__lt=days_ago) \
                              .filter(expired_at__isnull=True)
            for job in jobs:
                job.expire()

            msg = "[%s] %s jobs expired" % (site.name, len(jobs))
            self.stdout.write(self.style.SUCCESS(msg))
