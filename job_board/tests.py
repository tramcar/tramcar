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
