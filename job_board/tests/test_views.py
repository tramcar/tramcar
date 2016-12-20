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
    def setUp(self):
        category = Category(name='Software Development', site_id=1)
        category.full_clean()
        category.save()

    def test_index_view(self):
        response = self.client.get(reverse('categories_index'))
        self.assertEqual(response.status_code, 200)

    def test_show_view(self):
        response = self.client.get(reverse('categories_show', args=(1,)))
        self.assertEqual(response.status_code, 200)


class CompanyUnauthdViewTests(TestCase):
    def setUp(self):
        user = User(username='admin')
        user.set_password('password')
        user.full_clean()
        user.save()
        self.company = Company(name='Tramcar', url='http://www.tramcar.org',
                               site_id=1, user_id=user.id)
        self.company.full_clean()
        self.company.save()

    def test_index_view(self):
        response = self.client.get(reverse('companies_index'))
        self.assertEqual(response.status_code, 200)

    def test_new_view(self):
        response = self.client.get(reverse('companies_new'))
        self.assertRedirects(response, '/login/?next=/companies/new')

    def test_show_view(self):
        response = self.client.get(
                       reverse('companies_show', args=(self.company.id,))
                   )
        self.assertEqual(response.status_code, 200)

    def test_show_view_does_not_display_edit_link(self):
        response = self.client.get(
                       reverse('companies_show', args=(self.company.id,))
                   )
        url = reverse('companies_edit', args=(self.company.id,))
        edit = '<a class="btn btn-primary btn-sm" ' \
               'href="%s">Edit Company</a>' % url
        self.assertNotContains(response, edit)

    def test_edit_view(self):
        response = self.client.get(
                       reverse('companies_edit', args=(self.company.id,))
                   )
        url = reverse('companies_edit', args=(self.company.id,))
        self.assertRedirects(response, '/login/?next=%s' % url)


class CompanyAuthdViewTests(TestCase):
    def setUp(self):
        password = 'password'
        owner = User(username='owner')
        owner.set_password(password)
        owner.full_clean()
        owner.save()

        other = User(username='other')
        other.set_password(password)
        other.full_clean()
        other.save()

        self.company1 = Company(name='Tramcar', url='http://www.tramcar.org',
                                site_id=1, user_id=owner.id)
        self.company1.full_clean()
        self.company1.save()

        self.company2 = Company(name='WFH.io', url='https://www.wfh.io',
                                site_id=1, user_id=other.id)
        self.company2.full_clean()
        self.company2.save()

        self.client.post(
          '/login/',
          {'username': owner.username, 'password': password}
        )

    def test_index_view(self):
        response = self.client.get(reverse('companies_index'))
        self.assertEqual(response.status_code, 200)

    def test_new_view(self):
        response = self.client.get(reverse('companies_new'))
        self.assertEqual(response.status_code, 200)

    def test_show_view(self):
        response = self.client.get(
                       reverse('companies_show', args=(self.company1.id,))
                   )
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_own_company_shows_edit_link(self):
        response = self.client.get(
                       reverse('companies_show', args=(self.company1.id,))
                   )
        url = reverse('companies_edit', args=(self.company1.id,))
        edit = '<a class="btn btn-default btn-sm" ' \
               'href="%s">Edit Company</a>' % url
        self.assertContains(response, edit)

    def test_show_view_on_other_company_does_not_show_edit_link(self):
        response = self.client.get(
                       reverse('companies_show', args=(self.company2.id,))
                   )
        url = reverse('companies_edit', args=(self.company2.id,))
        edit = '<a class="btn btn-primary btn-sm" ' \
               'href="%s">Edit Company</a>' % url
        self.assertNotContains(response, edit)

    def test_edit_view(self):
        response = self.client.get(
                       reverse('companies_edit', args=(self.company1.id,))
                   )
        self.assertEqual(response.status_code, 200)


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

    def test_show_view_does_not_show_job_admin(self):
        response = self.client.get(reverse('jobs_show', args=(self.job.id,)))
        self.assertNotContains(response, 'Job Admin')

    def test_show_view_does_not_show_owner_email_address(self):
        response = self.client.get(reverse('jobs_show', args=(self.job.id,)))
        self.assertNotContains(response, self.job.email)

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
        password = 'password'
        owner = User(username='owner')
        owner.set_password(password)
        owner.full_clean()
        owner.save()

        other = User(username='otheruser')
        other.set_password(password)
        other.full_clean()
        other.save()

        country = Country(name='Canada')
        country.full_clean()
        country.save()

        company = Company(name='Tramcar', site_id=1, user_id=owner.id,
                          url='http://www.tramcar.org')
        company.full_clean()
        company.save()

        category = Category(name='Software Development', site_id=1)
        category.full_clean()
        category.save()

        self.job1 = Job(title='Software Developer',
                        description='Test description',
                        application_info='test', category_id=category.id,
                        company_id=company.id, site_id=1, user_id=owner.id,
                        city='Toronto', state='Ontario',
                        email='admin@tramcar.org')
        self.job1.full_clean()
        self.job1.save()
        self.job1.activate()

        self.job2 = Job(title='QA Engineer',
                        description='Test description',
                        application_info='test', category_id=category.id,
                        company_id=company.id, site_id=1, user_id=other.id,
                        city='Toronto', state='Ontario',
                        email='admin@tramcar.org')
        self.job2.full_clean()
        self.job2.save()
        self.job2.activate()

        self.client.post(
          '/login/',
          {'username': owner.username, 'password': password}
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
        response1 = self.client.post(reverse('jobs_new'), job)
        # NOTE: We assume a redirect here is success, the response.url could be
        #       anything so eventually we should find a way to ensure it
        #       redirects to /jobs/2/ (for example)
        self.assertRedirects(response1, response1.url)

        response2 = self.client.get(response1.url)
        self.assertContains(
            response2,
            '<span class="label label-warning %>">Unpaid</span>'
        )

    def test_mine_view(self):
        response = self.client.get(reverse('jobs_mine'))
        self.assertEqual(response.status_code, 200)

    def test_mine_view_only_shows_my_jobs(self):
        response = self.client.get(reverse('jobs_mine'))
        self.assertNotContains(response, self.job2.title)

    def test_show_view(self):
        response = self.client.get(reverse('jobs_show', args=(self.job1.id,)))
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_own_job_shows_job_admin(self):
        response = self.client.get(reverse('jobs_show', args=(self.job1.id,)))
        self.assertContains(response, 'Job Admin')

    def test_show_view_on_own_job_does_not_show_admin_expire_button(self):
        response = self.client.get(reverse('jobs_show', args=(self.job1.id,)))
        url = reverse('jobs_expire', args=(self.job1.id,))
        expire = '<a href="%s" class="btn btn-default">Expire</a>' % url
        self.assertContains(response, expire)

    def test_show_view_on_own_job_shows_email_address(self):
        response = self.client.get(reverse('jobs_show', args=(self.job1.id,)))
        self.assertContains(response, self.job1.email)

    def test_show_view_on_other_job_does_not_show_job_admin(self):
        response = self.client.get(reverse('jobs_show', args=(self.job2.id,)))
        self.assertNotContains(response, 'Job Admin')

    def test_show_view_on_other_job_does_not_show_email_address(self):
        response = self.client.get(reverse('jobs_show', args=(self.job2.id,)))
        self.assertNotContains(response, self.job2.email)

    def test_activate_view(self):
        response = self.client.get(
                       reverse('jobs_activate', args=(self.job1.id,))
                   )
        self.assertRedirects(
            response, '/login/?next=/jobs/%s/activate' % self.job1.id
        )

    def test_expire_view(self):
        response = self.client.get(
                       reverse('jobs_expire', args=(self.job1.id,))
                   )
        self.assertRedirects(
            response, reverse('jobs_show', args=(self.job1.id,))
        )

    def test_edit_get_view(self):
        response = self.client.get(reverse('jobs_edit', args=(self.job1.id,)))
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
                       reverse('jobs_edit', args=(self.job1.id,)), job
                   )
        self.assertRedirects(
            response, reverse('jobs_show', args=(self.job1.id,))
        )


class JobViewAdminTests(TestCase):

    def setUp(self):
        password = 'password'
        admin = User(username='admin')
        admin.is_staff = True
        admin.set_password(password)
        admin.full_clean()
        admin.save()

        other = User(username='otheruser')
        other.set_password(password)
        other.full_clean()
        other.save()

        country = Country(name='Canada')
        country.full_clean()
        country.save()

        company = Company(name='Tramcar', site_id=1, user_id=other.id,
                          url='http://www.tramcar.org')
        company.full_clean()
        company.save()

        category = Category(name='Software Development', site_id=1)
        category.full_clean()
        category.save()

        self.job = Job(title='Software Developer',
                       description='Test description',
                       application_info='test', category_id=category.id,
                       company_id=company.id, site_id=1, user_id=other.id,
                       city='Toronto', state='Ontario',
                       email='admin@tramcar.org')
        self.job.full_clean()
        self.job.save()
        self.job.activate()

        self.client.post(
          '/login/',
          {'username': admin.username, 'password': password}
        )

    def test_activate_view(self):
        response1 = self.client.get(
                        reverse('jobs_activate', args=(self.job.id,))
                    )
        self.assertRedirects(
            response1, reverse('jobs_show', args=(self.job.id,))
        )

        response2 = self.client.get(
                        reverse('jobs_show', args=(self.job.id,))
                    )
        self.assertContains(
            response2,
            '<span class="label label-success %>">Paid</span>'
        )


class MiscViewTests(TestCase):

    def test_charge_view(self):
        # This is just testing that the view itself responds, we pass in a
        # non-existent job and the view will then redirect with a 404
        response = self.client.post(
                       reverse('charge'),
                       {'job_id': 1000}
                   )
        self.assertEqual(response.status_code, 404)

    def test_contact_get_view(self):
        response = self.client.get(reverse('contact'))
        self.assertEqual(response.status_code, 200)

    def test_contact_post_view(self):
        feedback = {
            'email': 'admin@tramcar.org',
            'subject': 'Hi there!',
            'message': 'How are you?'
        }
        response = self.client.post(reverse('contact'), feedback)
        self.assertRedirects(response, reverse('jobs_index'))

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
