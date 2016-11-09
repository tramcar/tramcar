from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import render

from job_board.forms import ContactForm, CssUserCreationForm
from job_board.models.site_config import SiteConfig


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            site = get_current_site(request)
            sc = SiteConfig.objects.filter(site=site).first()
            cd = form.cleaned_data
            # re-tag subject to make it more identifiable
            cd['subject'] = "[%s] %s" % (site.name.upper(), cd['subject'])
            send_mail(
                cd['subject'],
                cd['message'],
                cd['email'],
                [sc.admin_email],
                fail_silently=True
            )
            return HttpResponseRedirect(reverse('jobs_index'))
    else:
        form = ContactForm()

    title = 'Contact Us'
    return render(request, "job_board/contact.html", {
        'form': form, 'title': title,
    })


def register(request):
    if request.method == 'POST':
        form = CssUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('jobs_index'))
    else:
        form = CssUserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
