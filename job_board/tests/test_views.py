from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.conf import settings
from django.test import TestCase

from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.country import Country
from job_board.models.job import Job


# NOTE: This seems counter-intuitive as we do not set a SITE_ID in settings.py,
#       however if we do not do this then the tests fail since the requests
#       don't match an existing site.  If we can figure out how to trick the
#       runner into using http://tramcar.org or change the domain of our site
#       to localhost/127.0.0.1 then we may be able to avoid having to set this.
settings.SITE_ID = 1


class CategoryViewTests(TestCase):

    def test_index_view(self):
        response = self.client.get(reverse('categories_index'))
        self.assertEqual(response.status_code, 200)

    def test_show_view(self):
        response = self.client.get(reverse('categories_show', args=(1,)))
        self.assertEqual(response.status_code, 200)


class CompanyViewTests(TestCase):

    def test_index_view(self):
        response = self.client.get(reverse('companies_index'))
        self.assertEqual(response.status_code, 200)

    def test_new_view(self):
        response = self.client.get(reverse('companies_new'))
        self.assertRedirects(response, '/login/?next=/companies/new')

    def test_show_view(self):
        response = self.client.get(reverse('companies_show', args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_edit_view(self):
        response = self.client.get(reverse('companies_edit', args=(1,)))
        self.assertRedirects(response, '/login/?next=/companies/1/edit')


class JobViewUnauthdTests(TestCase):

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
        self.job = Job(title='Software Developer',
                       description='Test description',
                       application_info='test', category_id=category.id,
                       company_id=company.id, site_id=1, user_id=user.id,
                       city='Toronto', state='Ontario',
                       email='admin@tramcar.org')
        self.job.full_clean()
        self.job.save()
        self.job.activate()

    def test_index_view(self):
        response = self.client.get(reverse('jobs_index'))
        self.assertEqual(response.status_code, 200)

    def test_new_view(self):
        response = self.client.get(reverse('jobs_new'))
        self.assertRedirects(response, '/login/?next=/jobs/new/')

    def test_mine_view(self):
        response = self.client.get(reverse('jobs_mine'))
        self.assertRedirects(response, '/login/?next=/jobs/mine/')

    def test_show_view(self):
        response = self.client.get(reverse('jobs_show', args=(self.job.id,)))
        self.assertEqual(response.status_code, 200)

    def test_activate_view(self):
        response = self.client.get(
                       reverse('jobs_activate', args=(self.job.id,))
                   )
        self.assertRedirects(
            response, '/login/?next=/jobs/%s/activate' % self.job.id
        )

    def test_expire_view(self):
        response = self.client.get(reverse('jobs_expire', args=(self.job.id,)))
        self.assertRedirects(
            response, '/login/?next=/jobs/%s/expire' % self.job.id
        )

    def test_edit_view(self):
        response = self.client.get(reverse('jobs_edit', args=(self.job.id,)))
        self.assertRedirects(
            response, '/login/?next=/jobs/%s/edit' % self.job.id
        )


class JobViewAuthdTests(TestCase):

    def setUp(self):
        user = User(username='admin')
        user.set_password('password')
        user.full_clean()
        user.save()
        country = Country(name='Canada')
        country.full_clean()
        country.save()
        company = Company(name='Tramcar', site_id=1, user_id=user.id,
                          url='http://www.tramcar.org')
        company.full_clean()
        company.save()
        category = Category(name='Software Development', site_id=1)
        category.full_clean()
        category.save()
        self.job = Job(title='Software Developer',
                       description='Test description',
                       application_info='test', category_id=category.id,
                       company_id=company.id, site_id=1, user_id=user.id,
                       city='Toronto', state='Ontario',
                       email='admin@tramcar.org')
        self.job.full_clean()
        self.job.save()
        self.job.activate()

        self.client.post(
          '/login/',
          {'username': 'admin', 'password': 'password'}
        )

    def test_index_view(self):
        response = self.client.get(reverse('jobs_index'))
        self.assertEqual(response.status_code, 200)

    def test_new_get_view(self):
        response = self.client.get(reverse('jobs_new'))
        self.assertEqual(response.status_code, 200)

    def test_new_post_view(self):
        job = {
            'title': 'DevOps Engineer',
            'description': 'testing',
            'application_info': 'testing',
            'email': 'admin@tramcar.org',
            'category': 1,
            'company': 1,
            'country': 1,
            'state': 'Ontario',
            'city': 'Guelph',
        }
        response = self.client.post(reverse('jobs_new'), job)
        # NOTE: We assume a redirect here is success, the response.url could be
        #       anything so eventually we should find a way to ensure it
        #       redirects to /jobs/2/ (for example)
        self.assertRedirects(response, response.url)

    def test_mine_view(self):
        response = self.client.get(reverse('jobs_mine'))
        self.assertEqual(response.status_code, 200)

    def test_show_view(self):
        response = self.client.get(reverse('jobs_show', args=(self.job.id,)))
        self.assertEqual(response.status_code, 200)

    # TODO: Test this w/ an admin user
    def test_activate_view(self):
        response = self.client.get(
                       reverse('jobs_activate', args=(self.job.id,))
                   )
        self.assertRedirects(
            response, '/login/?next=/jobs/%s/activate' % self.job.id
        )

    def test_expire_view(self):
        response = self.client.get(reverse('jobs_expire', args=(self.job.id,)))
        self.assertRedirects(
            response, reverse('jobs_show', args=(self.job.id,))
        )

    def test_edit_get_view(self):
        response = self.client.get(reverse('jobs_edit', args=(self.job.id,)))
        self.assertEqual(response.status_code, 200)

    def test_edit_post_view(self):
        job = {
            'title': 'Software Engineer',
            'description': 'testing',
            'application_info': 'testing',
            'email': 'admin@tramcar.org',
            'category': 1,
            'company': 1,
            'country': 1,
            'state': 'Ontario',
            'city': 'Guelph'
        }
        response = self.client.post(
                       reverse('jobs_edit', args=(self.job.id,)), job
                   )
        self.assertRedirects(
            response, reverse('jobs_show', args=(self.job.id,))
        )


class MiscViewTests(TestCase):

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
