from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site
from django.core.exceptions import ObjectDoesNotExist

from mailchimp3 import MailChimp


class Command(BaseCommand):
    help = 'Display all MailChimp lists'

    def add_arguments(self, parser):
        parser.add_argument('site_domain', nargs=1, type=str)

    def handle(self, *args, **options):
        site_domain = options['site_domain'][0]

        try:
            site = Site.objects.get(domain=site_domain)
        except ObjectDoesNotExist:
            raise CommandError(
                    'Site with domain name %s does not exist' % site_domain
                  )
        else:
            if (site.siteconfig.mailchimp_username and
                    site.siteconfig.mailchimp_api_key):

                client = MailChimp(
                             site.siteconfig.mailchimp_username,
                             site.siteconfig.mailchimp_api_key
                         )

                try:
                    lists = client.lists.all()
                except Exception:
                    raise CommandError(
                            'There was a problem connecting to the MailChimp '
                            'API, check your credentials and try again'
                          )

                if len(lists['lists']) > 0:
                    msg = "The following MailChimp lists exist:\n"
                    msg += "ID\t\tName\n"

                    for list in lists['lists']:
                        msg += "%s\t%s\n" % (list['id'], list['name'])
                    self.stdout.write(self.style.SUCCESS(msg))
                else:
                    msg = "No lists were found for site with domain " \
                          "name %s" % site_domain
                    self.stdout.write(self.style.NOTICE(msg))
            else:
                raise CommandError(
                          'A MailChimp username and or api_key have '
                          'not been configured on the site with domain '
                          'name %s' % site_domain
                      )
