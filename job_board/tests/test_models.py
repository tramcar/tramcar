from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from django.test import TestCase

from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.job import Job
from job_board.models.user_token import UserToken

# NOTE: This seems counter-intuitive as we do not set a SITE_ID in settings.py,
#       however if we do not do this then the tests fail since the requests
#       don't match an existing site.  If we can figure out how to trick the
#       runner into using http://tramcar.org or change the domain of our site
#       to localhost/127.0.0.1 then we may be able to avoid having to set this.
settings.SITE_ID = 1


class SiteConfigMethodTests(TestCase):
    def setUp(self):
        # Note that we're assigning non-existent values for country,
        # category, etc.
        self.site = Site(domain='tramcar.org', name='Tramcar')
        self.site.full_clean()
        self.site.save()
        self.site.siteconfig.price = 50.25
        self.site.siteconfig.full_clean()
        self.site.siteconfig.save()

    def test_price_in_cents_returns_correct_value(self):
        self.assertEqual(self.site.siteconfig.price_in_cents(), 5025)
        self.assertIsInstance(self.site.siteconfig.price_in_cents(), int)


class SiteMethodTests(TestCase):
    def setUp(self):
        # Note that we're assigning non-existent values for country,
        # category, etc.
        site = Site(domain='tramcar.org', name='Tramcar')
        site.full_clean()
        site.save()

    def test_site_config_entry_exists(self):
        site = Site.objects.get(name='Tramcar')
        # NOTE: We use .first() here so we get None when there is no match,
        #       rather than an exception being raised.
        self.assertIsNotNone(site.siteconfig)

    def test_site_config_has_correct_defaults(self):
        site = Site.objects.get(name='Tramcar')
        self.assertEqual(site.siteconfig.expire_after, 30)
        self.assertEqual(site.siteconfig.admin_email, 'admin@tramcar.org')


class CompanyMethodTests(TestCase):
    def setUp(self):
        self.user = User(username='admin')
        self.user.set_password('password')
        self.user.full_clean()
        self.user.save()
        self.company = Company(name='Tramcar', site_id=1, user_id=self.user.id,
                               url='http://www.tramcar.org')
        self.company.full_clean()
        self.company.save()
        self.category = Category(name='Software Development', site_id=1)
        self.category.full_clean()
        self.category.save()

    def test_active_jobs(self):
        job = Job(title='Software Developer',
                  description='Test description',
                  application_info='test', category_id=self.category.id,
                  company_id=self.company.id, site_id=1, user_id=self.user.id,
                  city='Toronto', state='Ontario',
                  email='admin@tramcar.org')
        job.full_clean()
        job.save()
        self.assertEqual(len(self.company.active_jobs()), 0)
        job.activate()
        self.assertEqual(len(self.company.active_jobs()), 1)

    def test_paid_jobs(self):
        job = Job(title='Software Developer',
                  description='Test description',
                  application_info='test', category_id=self.category.id,
                  company_id=self.company.id, site_id=1, user_id=self.user.id,
                  city='Toronto', state='Ontario',
                  email='admin@tramcar.org')
        job.full_clean()
        job.save()
        self.assertEqual(len(self.company.paid_jobs()), 0)
        job.activate()
        self.assertEqual(len(self.company.paid_jobs()), 1)


class JobMethodTests(TestCase):
    def setUp(self):
        user = User(username='admin')
        user.set_password('password')
        user.full_clean()
        user.save()
        company = Company(name='Tramcar', url='http://www.tramcar.org',
                          site_id=1, user_id=user.id)
        company.full_clean()
        company.save()
        category = Category(name='Software Development', site_id=1)
        category.full_clean()
        category.save()
        job = Job(title='Software Developer',
                  description='Test description',
                  application_info='test', category_id=category.id,
                  company_id=company.id, site_id=1, user_id=user.id,
                  city='Toronto', state='Ontario',
                  email='admin@tramcar.org')
        job.paid_at = job.created_at
        job.full_clean()
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


class UserTokenMethodTests(TestCase):
    def setUp(self):
        self.user = User(username='admin')
        self.user.set_password('password')
        self.user.full_clean()
        self.user.save()

    def test_deduct_token(self):
        self.tokens = UserToken(user=self.user, tokens=10)
        self.tokens.full_clean()
        self.tokens.save()

        self.tokens.deduct()

        self.assertEqual(9, self.tokens.tokens)
