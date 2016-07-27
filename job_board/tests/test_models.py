from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase

from job_board.models import Company, Job, Site, SiteConfig

# NOTE: This seems counter-intuitive as we do not set a SITE_ID in settings.py,
#       however if we do not do this then the tests fail since the requests
#       don't match an existing site.  If we can figure out how to trick the
#       runner into using http://tramcar.org or change the domain of our site
#       to localhost/127.0.0.1 then we may be able to avoid having to set this.
settings.SITE_ID = 1


class SiteMethodTests(TestCase):
    def setUp(self):
        # Note that we're assigning non-existent values for country,
        # category, etc.
        site = Site(domain='tramcar.org', name='Tramcar')
        site.save()

    def test_site_config_entry_exists(self):
        site = Site.objects.get(name='Tramcar')
        # NOTE: We use .first() here so we get None when there is no match,
        #       rather than an exception being raised.
        sc = SiteConfig.objects.filter(site=site).first()
        self.assertIsNotNone(sc)

    def test_site_config_has_correct_defaults(self):
        site = Site.objects.get(name='Tramcar')
        sc = SiteConfig.objects.filter(site=site).first()
        self.assertEqual(sc.expire_after, 30)
        self.assertEqual(sc.admin_email, 'admin@tramcar.org')


class CompanyMethodTests(TestCase):
    def setUp(self):
        # Note that we're assigning non-existent values for country,
        # category, etc.
        company = Company(name='Tramcar', site_id=1, user_id=1)
        company.save()

    def test_active_jobs(self):
        company = Company.objects.get(name='Tramcar')
        job = Job(title='Software Developer', country_id=1,
                  category_id=1, company_id=company.id, site_id=1,
                  user_id=1)
        job.save()
        self.assertEqual(len(company.active_jobs()), 0)
        job.activate()
        self.assertEqual(len(company.active_jobs()), 1)

    def test_paid_jobs(self):
        company = Company.objects.get(name='Tramcar')
        job = Job(title='Software Developer', country_id=1,
                  category_id=1, company_id=company.id, site_id=1,
                  user_id=1)
        job.save()
        self.assertEqual(len(company.paid_jobs()), 0)
        job.activate()
        self.assertEqual(len(company.paid_jobs()), 1)


class JobMethodTests(TestCase):
    def setUp(self):
        # Note that we're assigning non-existent values for country,
        # category, etc.
        job = Job(title='Software Developer', country_id=1, category_id=1,
                  company_id=1, site_id=1, user_id=1)
        job.paid_at = job.created_at
        job.save()

    def test_activate_on_unactivated_job(self):
        job = Job.objects.get(title='Software Developer')
        self.assertTrue(job.activate())
        self.assertIsNotNone(job.paid_at)

    def test_activate_on_already_activated_job(self):
        job = Job.objects.get(title='Software Developer')
        job.activate()
        paid_at = job.paid_at
        self.assertFalse(job.activate())
        self.assertEqual(paid_at, job.paid_at)

    def test_expire_on_unexpired_job(self):
        job = Job.objects.get(title='Software Developer')
        job.activate()
        self.assertTrue(job.expire())
        self.assertIsNotNone(job.expired_at)

    def test_expire_on_already_expired_job(self):
        job = Job.objects.get(title='Software Developer')
        job.activate()
        job.expire()
        expired_at = job.expired_at
        self.assertFalse(job.expire())
        self.assertEqual(expired_at, job.expired_at)

    def test_expire_on_unactivated_job(self):
        job = Job.objects.get(title='Software Developer')
        self.assertFalse(job.expire())
        self.assertIsNone(job.expired_at)
