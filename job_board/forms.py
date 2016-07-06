from django.forms import ModelForm
from job_board.models import Company, Job


class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['company', 'title', 'description', 'application_info',
                  'location', 'email', 'category', 'country']


class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'url', 'country', 'twitter']
