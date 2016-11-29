from django.core.urlresolvers import reverse
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from utils.misc import send_mail_with_helper

from job_board.forms import ContactForm, CssUserCreationForm
from job_board.models.job import Job
from job_board.models.site_config import SiteConfig

import stripe


def charge(request):
    if request.method == 'POST':
        site = get_current_site(request)
        sc = SiteConfig.objects.filter(site=site).first()
        stripe.api_key = sc.stripe_secret_key
        job = get_object_or_404(
                  Job,
                  pk=request.POST['job_id'],
                  site_id=site.id,
                  user_id=request.user.id
              )

        token = request.POST['stripeToken']

        try:
            desc = '%s Job Posting (%s://%s/jobs/%s)' % (
                       site.name, sc.protocol, site.domain, job.id
                   )
            charge = stripe.Charge.create(
                source=token,
                amount=sc.price_in_cents(),
                currency='usd',
                description=desc,
                receipt_email=request.user.email
            )
        # NOTE: With checkout.js, it seems that all the error handling is
        #       handled on the front-end, so perhaps we do not need to worry
        #       about handling this exception.
        except stripe.error.CardError as e:
            body = e.json_body
            err = body['error']
            messages.error(request, err['message'])
            return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))
        else:
            if charge['paid']:
                job.activate()
                messages.success(
                    request,
                    ("Thank you, your payment of $%s has been received and "
                     "your job is now active" % sc.price)
                )

        return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            site = get_current_site(request)
            sc = SiteConfig.objects.filter(site=site).first()
            cd = form.cleaned_data
            # re-tag subject to make it more identifiable
            cd['subject'] = "[%s] %s" % (site.name.upper(), cd['subject'])
            send_mail_with_helper(
                cd['subject'],
                cd['message'],
                cd['email'],
                [sc.admin_email]
            )

            messages.success(
                request,
                "Thank you for your message, "
                "we'll be back in touch as soon as possible"
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

            messages.success(
                request,
                'Your account has been successfully created, '
                'please log in to continue'
            )

            return HttpResponseRedirect(reverse('jobs_index'))
    else:
        form = CssUserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
