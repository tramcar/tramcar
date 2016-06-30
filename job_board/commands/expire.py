from datetime import timedelta

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from job_board.models import Job, Site

class Command(BaseCommand):
    help = 'Expire all jobs older than 30 days'

    def handle(self, *args, **options):
        days_ago = timezone.now() - timedelta(days=30)
        jobs = Job.objects.filter(paid_at__lt=days_ago, expired_at__isnull=True)
        for job in jobs:
            job.expired_at = timezone.now()
            job.save()

        if jobs:
            self.stdout.write(self.style.SUCCESS('Successfully expired %s jobs' % len(jobs)))
