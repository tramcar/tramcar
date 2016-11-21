from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django import forms

from job_board.models.company import Company
from job_board.models.job import Job


class ContactForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['subject'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['message'].widget.attrs['class'] = 'form-control'

    email = forms.EmailField(label='Your e-mail address')
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)


class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['company'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['application_info'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['city'].widget.attrs['class'] = 'form-control'
        self.fields['state'].widget.attrs['class'] = 'form-control'
        self.fields['location'].widget.attrs['class'] = 'form-control'
        self.fields['remote'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Job
        fields = ['company', 'title', 'description', 'application_info',
                  'remote', 'city', 'state', 'country', 'location', 'email',
                  'category']


class JobRemoteForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(JobRemoteForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['company'].widget.attrs['class'] = 'form-control'
        self.fields['title'].widget.attrs['class'] = 'form-control'
        self.fields['description'].widget.attrs['class'] = 'form-control'
        self.fields['application_info'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['location'].widget.attrs['class'] = 'form-control'
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['category'].widget.attrs['class'] = 'form-control'

    class Meta:
        model = Job
        fields = ['company', 'title', 'description', 'application_info',
                  'country', 'location', 'email', 'category']


class CompanyForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(CompanyForm, self).__init__(*args, **kwargs)
        self.label_suffix = ''
        self.fields['name'].widget.attrs['class'] = 'form-control'
        self.fields['url'].widget.attrs['class'] = 'form-control'
        self.fields['country'].widget.attrs['class'] = 'form-control'
        self.fields['twitter'].widget.attrs['class'] = 'form-control'
        self.fields['site'].widget = forms.HiddenInput()

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
        self.fields['email'].widget.attrs['class'] = 'form-control'
        self.fields['password1'].widget.attrs['class'] = 'form-control'
        self.fields['password2'].widget.attrs['class'] = 'form-control'

    # UserCreationForm doesn't include email, so we add it and make it required
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    email = forms.EmailField(required=True)
