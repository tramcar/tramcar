from django.contrib.auth.models import User
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.country import Country
from job_board.models.job import Job
from job_board.models.user_token import UserToken


# NOTE: This seems counter-intuitive as we do not set a SITE_ID in settings.py,
#       however if we do not do this then the tests fail since the requests
#       don't match an existing site.  If we can figure out how to trick the
#       runner into using http://tramcar.org or change the domain of our site
#       to localhost/127.0.0.1 then we may be able to avoid having to set this.
settings.SITE_ID = 1


class CategoryViewTests(TestCase):
    def setUp(self):
        self.category = Category(name='Software Development', site_id=1)
        self.category.full_clean()
        self.category.save()

    def test_index_view(self):
        response = self.client.get(reverse('categories_index'))
        self.assertEqual(response.status_code, 200)

    def test_show_view(self):
        response = self.client.get(self.category.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_without_slug_redirects_to_slug(self):
        response = self.client.get(
                       reverse('categories_show', args=(self.category.id,))
                   )
        self.assertRedirects(
            response, self.category.get_absolute_url(), status_code=301
        )


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
        response = self.client.get(self.company.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_without_slug_redirects_to_slug(self):
        response = self.client.get(
                       reverse('companies_show', args=(self.company.id,))
                   )
        self.assertRedirects(
            response, self.company.get_absolute_url(), status_code=301
        )

    def test_show_view_does_not_display_edit_link(self):
        response = self.client.get(self.company.get_absolute_url())
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
        response = self.client.get(self.company1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_own_company_shows_edit_link(self):
        response = self.client.get(self.company1.get_absolute_url())
        url = reverse('companies_edit', args=(self.company1.id,))
        edit = '<a class="btn btn-default btn-sm" ' \
               'href="%s">Edit Company</a>' % url
        self.assertContains(response, edit)

    def test_show_view_on_other_company_does_not_show_edit_link(self):
        response = self.client.get(self.company2.get_absolute_url())
        url = reverse('companies_edit', args=(self.company2.id,))
        edit = '<a class="btn btn-primary btn-sm" ' \
               'href="%s">Edit Company</a>' % url
        self.assertNotContains(response, edit)

    def test_edit_view(self):
        response = self.client.get(
                       reverse('companies_edit', args=(self.company1.id,))
                   )
        self.assertEqual(response.status_code, 200)


class CompanyAdminViewTests(TestCase):
    def setUp(self):
        password = 'password'
        owner = User(username='owner')
        owner.set_password(password)
        owner.full_clean()
        owner.save()

        admin = User(username='admin')
        admin.is_staff = True
        admin.set_password(password)
        admin.full_clean()
        admin.save()

        self.company = Company(name='Tramcar', url='http://www.tramcar.org',
                               site_id=1, user_id=owner.id)
        self.company.full_clean()
        self.company.save()

        self.client.post(
          '/login/',
          {'username': admin.username, 'password': password}
        )

    def test_edit_get_view(self):
        response = self.client.get(
                       reverse('companies_edit', args=(self.company.id,))
                   )
        self.assertEqual(response.status_code, 200)

    def test_edit_post_view(self):
        company = {
            'name': 'Tramcar',
            'url': 'https://www.tramcar.org',
            'site': 1,
            'user': 1
        }
        response = self.client.post(
                       reverse('companies_edit', args=(self.company.id,)),
                       company
                   )
        # Here we refresh the object otherwise it will show the old content
        # from before the update
        self.company.refresh_from_db()
        self.assertRedirects(response, self.company.get_absolute_url())


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
        response = self.client.get(self.job.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_without_slug_redirects_to_slug(self):
        response = self.client.get(
                       reverse('jobs_show', args=(self.job.id,))
                   )
        self.assertRedirects(
            response, self.job.get_absolute_url(), status_code=301
        )

    def test_show_view_does_not_show_job_admin(self):
        response = self.client.get(self.job.get_absolute_url())
        self.assertNotContains(response, 'Job Admin')

    def test_show_view_does_not_show_owner_email_address(self):
        response = self.client.get(self.job.get_absolute_url())
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

        self.job3 = Job(title='DevOps Engineer',
                        description='Test description',
                        application_info='test', category_id=category.id,
                        company_id=company.id, site_id=1, user_id=other.id,
                        city='Toronto', state='Ontario',
                        email='admin@tramcar.org')
        self.job3.full_clean()
        self.job3.save()

        self.job4 = Job(title='Growth Hacker',
                        description='Test description',
                        application_info='test', category_id=category.id,
                        company_id=company.id, site_id=1, user_id=owner.id,
                        city='Toronto', state='Ontario',
                        email='admin@tramcar.org')
        self.job4.full_clean()
        self.job4.save()

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
        response = self.client.post(reverse('jobs_new'), job)
        # NOTE: We assume a redirect here is success, the response.url could be
        #       anything so eventually we should find a way to ensure it
        #       redirects to /jobs/2/ (for example)
        self.assertRedirects(response, response.url)

    def test_mine_view(self):
        response = self.client.get(reverse('jobs_mine'))
        self.assertEqual(response.status_code, 200)

    def test_mine_view_only_shows_my_jobs(self):
        response = self.client.get(reverse('jobs_mine'))
        self.assertNotContains(response, self.job2.title)

    def test_show_view_on_own_paid_job(self):
        response = self.client.get(self.job1.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_own_unpaid_job(self):
        response = self.client.get(self.job4.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_own_unpaid_job_shows_unpaid_status(self):
        response = self.client.get(self.job4.get_absolute_url())
        self.assertContains(
            response,
            '<span class="label label-warning">Unpaid</span>'
        )

    def test_show_view_on_other_users_paid_job(self):
        response = self.client.get(self.job2.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_other_users_unpaid_job(self):
        response = self.client.get(self.job3.get_absolute_url())
        self.assertEqual(response.status_code, 404)

    def test_show_view_on_own_job_shows_job_admin(self):
        response = self.client.get(self.job1.get_absolute_url())
        self.assertContains(response, 'Job Admin')

    def test_show_view_on_own_job_does_not_show_posted_by(self):
        response = self.client.get(self.job1.get_absolute_url())
        posted_by = '<h4><mark>Posted By</mark></h4>'
        self.assertNotContains(response, posted_by)

    def test_show_view_on_own_job_shows_expire_button(self):
        response = self.client.get(self.job1.get_absolute_url())
        url = reverse('jobs_expire', args=(self.job1.id,))
        expire = '<a href="%s" class="btn btn-default">Expire</a>' % url
        self.assertContains(response, expire)

    def test_show_view_on_own_job_does_not_show_admin_activate_button(self):
        response = self.client.get(self.job1.get_absolute_url())
        url = reverse('jobs_activate', args=(self.job1.id,))
        activate = '<a href="%s" class="btn btn-default">Activate</a>' % url
        self.assertNotContains(response, activate)

    def test_show_view_on_own_job_shows_email_address(self):
        response = self.client.get(self.job1.get_absolute_url())
        self.assertContains(response, self.job1.email)

    def test_show_view_on_other_job_does_not_show_job_admin(self):
        response = self.client.get(self.job2.get_absolute_url())
        self.assertNotContains(response, 'Job Admin')

    def test_show_view_on_other_job_does_not_show_email_address(self):
        response = self.client.get(self.job2.get_absolute_url())
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
        self.assertRedirects(response, self.job1.get_absolute_url())

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
                       reverse('jobs_edit', args=(self.job1.id,)),
                       job
                   )
        # Here we refresh the object otherwise it will show the old content
        # from before the update
        self.job1.refresh_from_db()
        self.assertRedirects(response, self.job1.get_absolute_url())


class JobViewAdminTests(TestCase):

    def setUp(self):
        password = 'password'
        admin = User(username='admin')
        admin.is_staff = True
        admin.set_password(password)
        admin.full_clean()
        admin.save()

        self.other = User(username='otheruser')
        self.other.set_password(password)
        self.other.full_clean()
        self.other.save()

        country = Country(name='Canada')
        country.full_clean()
        country.save()

        company = Company(name='Tramcar', site_id=1, user_id=self.other.id,
                          url='http://www.tramcar.org')
        company.full_clean()
        company.save()

        category = Category(name='Software Development', site_id=1)
        category.full_clean()
        category.save()

        self.job = Job(title='Software Developer',
                       description='Test description',
                       application_info='test', category_id=category.id,
                       company_id=company.id, site_id=1, user_id=self.other.id,
                       city='Toronto', state='Ontario',
                       email='admin@tramcar.org')
        self.job.full_clean()
        self.job.save()

        self.client.post(
          '/login/',
          {'username': admin.username, 'password': password}
        )

    def test_activate_view(self):
        response1 = self.client.get(
                        reverse('jobs_activate', args=(self.job.id,))
                    )
        self.assertRedirects(response1, self.job.get_absolute_url())

        response2 = self.client.get(self.job.get_absolute_url())
        self.assertContains(
            response2,
            '<span class="label label-success">Paid</span>'
        )
        url = reverse('jobs_expire', args=(self.job.id,))
        expire = '<a href="%s" class="btn btn-default">Expire</a>' % url
        self.assertContains(
            response2,
            expire
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
                       reverse('jobs_edit', args=(self.job.id,)),
                       job
                   )
        # Here we refresh the object otherwise it will show the old content
        # from before the update
        self.job.refresh_from_db()
        self.assertRedirects(response, self.job.get_absolute_url())

    def test_show_view_shows_posted_by(self):
        response = self.client.get(self.job.get_absolute_url())
        header = '<h4><mark>Posted By</mark></h4>'
        posted_by = '<p>%s (UID: %s)</p>' % (self.other.username,
                                             self.other.id)
        self.assertContains(response, header)
        self.assertContains(response, posted_by)

    def test_show_view_on_other_users_unpaid_job(self):
        response = self.client.get(self.job.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_show_view_on_other_users_job_shows_email_address(self):
        response = self.client.get(self.job.get_absolute_url())
        self.assertContains(response, self.job.email)

    def test_show_view_on_other_users_job_shows_admin_activate_button(self):
        response = self.client.get(self.job.get_absolute_url())
        url = reverse('jobs_activate', args=(self.job.id,))
        activate = '<a href="%s" class="btn btn-default">Activate</a>' % url
        self.assertContains(response, activate)


class MiscViewTests(TestCase):

    def test_charge_card_get_view(self):
        response = self.client.get(reverse('charge_card'))
        self.assertRedirects(response, '/login/?next=/charge_card')

    def test_charge_token_get_view(self):
        response = self.client.get(reverse('charge_token'))
        self.assertRedirects(response, '/login/?next=/charge_token')

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


class MiscAuthdViewTests(TestCase):

    def setUp(self):
        password = 'password'
        user = User(username='owner')
        user.set_password(password)
        user.full_clean()
        user.save()
        ut = UserToken(user=user, tokens=1)
        ut.full_clean()
        ut.save()
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

        self.client.post(
          '/login/',
          {'username': user.username, 'password': password}
        )

    def test_charge_token_post_view(self):
        # We add follow=True here so we can follow the redirection and check
        # content of page without having to request it again
        response = self.client.post(
                       reverse('charge_token'),
                       {'job_id': self.job.id},
                       follow=True
                   )
        self.assertRedirects(
            response, self.job.get_absolute_url(), 302
        )
        self.assertContains(
            response,
            '<span class="label label-success">Paid</span>'
        )
