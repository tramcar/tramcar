from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from job_board.models import Job, Site


class Command(BaseCommand):
    help = 'Expire all jobs older than 30 days'

    def handle(self, *args, **options):
        days_ago = timezone.now() - timedelta(days=30)
        jobs = Job.objects.filter(paid_at__lt=days_ago) \
                          .filter(expired_at__isnull=True)
        for job in jobs:
            job.expire()

        if jobs:
            msg = "Successfully expired %s jobs" % len(jobs)
            self.stdout.write(self.style.SUCCESS(msg))
