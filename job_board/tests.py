from django.core.urlresolvers import reverse
from django.test import TestCase

from .models import Job


class JobViewTests(TestCase):

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
        response = self.client.get(reverse('jobs_show', args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_activate_view(self):
        response = self.client.get(reverse('jobs_activate', args=(1,)))
        self.assertRedirects(response, '/login/?next=/jobs/1/activate')

    def test_expire_view(self):
        response = self.client.get(reverse('jobs_expire', args=(1,)))
        self.assertRedirects(response, '/login/?next=/jobs/1/expire')

    def test_edit_view(self):
        response = self.client.get(reverse('jobs_edit', args=(1,)))
        self.assertRedirects(response, '/login/?next=/jobs/1/edit')


class CategoryViewTests(TestCase):

    def test_index_view(self):
        response = self.client.get(reverse('categories_index'))
        self.assertEqual(response.status_code, 200)

    def test_show_view(self):
        response = self.client.get(reverse('categories_show', args=(1,)))
        self.assertEqual(response.status_code, 404)


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
