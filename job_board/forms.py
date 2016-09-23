from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django import forms

from job_board.models.company import Company
from job_board.models.job import Job


class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['company'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['application_info'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['location'].widget.attrs['class'] = 'form-control'
        self.fields['remote'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Job
        fields = ['company', 'title', 'description', 'application_info',
                  'country', 'location', 'remote', 'email', 'category']


class CompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['twitter'].widget.attrs['class'] = 'form-control'
        self.fields['site'].widget=forms.HiddenInput()

    class Meta:
        model = Company
        fields = ['name', 'url', 'country', 'twitter', 'site']


class CssAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CssAuthenticationForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password'].widget.attrs['class'] = 'form-control'


class CssUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CssUserCreationForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['username'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'
