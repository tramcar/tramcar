from collections import OrderedDict
from datetime import timedelta

from mailchimp3 import MailChimp

from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils import timezone

from job_board.models.category import Category


class Command(BaseCommand):
    help = 'Send weekly mailshot e-mail'

    def handle(self, *args, **options):
        for site in Site.objects.all():
            sent = False
            if (site.siteconfig.mailchimp_username and
                    site.siteconfig.mailchimp_api_key and
                    site.siteconfig.mailchimp_list_id):
                jobs = OrderedDict()
                td = timedelta(days=7)
                days_ago = timezone.now() - td

                for c in Category.objects.filter(site=site).order_by('name'):
                    j = c.job_set.filter(paid_at__gt=days_ago) \
                                 .filter(expired_at__isnull=True) \
                                 .order_by('paid_at')

                    if len(j) > 0:
                        jobs[c.name] = j

                context = {'jobs': jobs, 'site': site}

                if len(jobs) > 0:
                    client = MailChimp(
                                 site.siteconfig.mailchimp_username,
                                 site.siteconfig.mailchimp_api_key
                             )
                    subject = '[%s] *ALL* jobs posted in the last ' \
                              '7 days' % site.name.upper()
                    data = {
                               'type': 'plaintext',
                               'recipients': {
                                   'list_id': site.siteconfig.mailchimp_list_id
                               },
                               'settings': {
                                   'subject_line': subject,
                                   'reply_to': site.siteconfig.admin_email,
                                   'from_name': '%s Weekly Mailer' % site.name
                               }
                           }

                    content = render_to_string(
                                  'job_board/emails/send_mailshot.txt',
                                  context
                              )

                    c = client.campaigns.create(data)
                    client.campaigns.content.update(
                        c['id'],
                        dict(plain_text=content)
                    )
                    client.campaigns.actions.send(c['id'])
                    sent = True

            msg = "[%s] mailshot sent: %s" % (site.name, sent)
            self.stdout.write(self.style.SUCCESS(msg))
