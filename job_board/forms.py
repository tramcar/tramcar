from django.forms import ModelForm
from job_board.models import Company, Job

class JobForm(ModelForm):
    class Meta:
        model = Job
        fields = ['title', 'description', 'application_info', 'location',
                  'email', 'category', 'country', 'company']

class CompanyForm(ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'url', 'country', 'twitter']
