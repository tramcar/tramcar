from django.forms import ModelForm

from job_board.models.company import Company
from job_board.models.job import Job


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['company', 'title', 'description', 'application_info',
                  'country', 'location', 'email', 'category']


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'url', 'country', 'twitter']
