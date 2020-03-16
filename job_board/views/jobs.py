from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import (Http404, HttpResponseRedirect,
                         HttpResponsePermanentRedirect)
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from utils.misc import convert_markdown, send_mail_with_helper

from job_board.forms import CompanyForm, JobForm, JobRemoteForm, SubscribeForm
from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.job import Job


def jobs_index(request):
    meta_desc = 'Browse a list of the most recently posted jobs'
    title = 'Latest Jobs'
    form = SubscribeForm()
    jobs = Job.objects.filter(site_id=get_current_site(request).id) \
                      .filter(paid_at__isnull=False) \
                      .filter(expired_at__isnull=True) \
                      .order_by('-paid_at')[:10]
    context = {'meta_desc': meta_desc,
               'title': title,
               'form': form,
               'jobs': jobs}
    return render(request, 'job_board/jobs_index.html', context)


@login_required(login_url='/login/')
def jobs_mine(request):
    jobs_list = Job.objects.filter(site_id=get_current_site(request).id) \
                           .filter(user_id=request.user.id) \
                           .order_by('-created_at')
    paginator = Paginator(jobs_list, 25)
    page = request.GET.get('page')
    title = 'My Jobs'
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        jobs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        jobs = paginator.page(paginator.num_pages)
    context = {'jobs': jobs, 'title': title}
    return render(request, 'job_board/jobs_mine.html', context)


@login_required(login_url='/login/')
def jobs_new(request):
    title = 'Add a Job'
    site = get_current_site(request)
    msg = 'Your job has been successfully added'

    if request.method == 'POST':
        if site.siteconfig.remote:
            form = JobRemoteForm(request.POST)
        else:
            form = JobForm(request.POST)

        company_form = CompanyForm(initial={'site': site})

        if form.is_valid():
            job = form.save(commit=False)
            if site.siteconfig.remote:
                job.remote = True
            job.site_id = site.id
            job.user_id = request.user.id
            job.save()
            context = {'job': job, 'protocol': site.siteconfig.protocol}
            send_mail_with_helper(
                '[%s] New job posting' % site.name.upper(),
                render_to_string(
                    'job_board/emails/new_job_notification.txt',
                    context
                ),
                site.siteconfig.admin_email,
                [site.siteconfig.admin_email]
            )

            if site.siteconfig.price == 0:
                msg += ', however it does require verification ' \
                       'before being activated'

            messages.success(request, msg)

            return HttpResponseRedirect(job.get_absolute_url())
    else:
        if site.siteconfig.remote:
            form = JobRemoteForm()
        else:
            form = JobForm()

        company_form = CompanyForm(initial={'site': site})

    # NOTE: By default, the company and category dropdowns will contain all
    #       instances across all sites, and the following limits this to
    #       the site in question.
    form.fields['company'].queryset = Company.objects.filter(
                                          site_id=site.id
                                      )
    form.fields['category'].queryset = Category.objects.filter(
                                          site_id=site.id
                                       )

    context = {'form': form,
               'company_form': company_form,
               'title': title,
               'protocol': site.siteconfig.protocol}
    return render(request, 'job_board/jobs_new.html', context)


def jobs_show(request, job_id, slug=None):
    job = get_object_or_404(
              Job, pk=job_id, site_id=get_current_site(request).id
          )

    if slug is None:
        return HttpResponsePermanentRedirect(job.get_absolute_url())

    site = get_current_site(request)
    # If the browsing user does not own the job, and the job has yet to be paid
    # for, then 404
    if (job.user.id != request.user.id and not request.user.is_staff and
            job.paid_at is None):
        raise Http404("No Job matches the given query.")
    # If someone views an unpaid job (job owner or admin), display the job's
    # created_at date instead of paid_at
    if job.paid_at is None:
        post_date = job.created_at
    else:
        post_date = job.paid_at
    job.description_md = convert_markdown(job.description)
    job.application_info_md = convert_markdown(job.application_info)
    job.remote = "Yes" if job.remote else "No"
    if job.remote == "Yes":
        meta_desc = '%s is hiring a remote %s. Apply today!' % \
                    (job.company.name, job.title)
    else:
        meta_desc = '%s is hiring a %s in %s, %s. Apply today!' % \
                    (job.company.name, job.title, job.city, job.state)
    title = "%s @ %s" % (job.title, job.company.name)
    stripe_key = site.siteconfig.stripe_publishable_key

    tokens = 0
    if hasattr(job.user, 'usertoken'):
        if job.user.usertoken.tokens > 0:
            tokens = job.user.usertoken.tokens

    context = {'job': job,
               'post_date': post_date,
               'meta_desc': meta_desc,
               'title': title,
               'remote': site.siteconfig.remote,
               'stripe_publishable_key': stripe_key,
               'price': site.siteconfig.price,
               'price_in_cents': site.siteconfig.price_in_cents(),
               'tokens': tokens}
    return render(request, 'job_board/jobs_show.html', context)


@login_required(login_url='/login/')
def jobs_edit(request, job_id):
    site = get_current_site(request)
    protocol = site.siteconfig.protocol
    job = get_object_or_404(
              Job, pk=job_id, site_id=site.id
          )
    title = 'Edit a Job'

    if (request.user.id != job.user.id) and not request.user.is_staff:
        return HttpResponseRedirect(job.get_absolute_url())

    if request.method == 'POST':
        if site.siteconfig.remote:
            form = JobRemoteForm(request.POST, instance=job)
        else:
            form = JobForm(request.POST, instance=job)

        if form.is_valid():
            job = form.save(commit=False)
            job.site_id = site.id
            job.user_id = request.user.id
            if site.siteconfig.remote:
                job.remote = True

            job.save()

            messages.success(request, 'Your job has been successfully updated')

            return HttpResponseRedirect(job.get_absolute_url())
    else:
        if site.siteconfig.remote:
            form = JobRemoteForm(instance=job)
        else:
            form = JobForm(instance=job)

    form.fields['company'].queryset = Company.objects.filter(
                                          site_id=site.id
                                      )
    form.fields['category'].queryset = Category.objects.filter(
                                           site_id=site.id
                                       )

    context = {'form': form, 'job': job, 'title': title, 'protocol': protocol}

    return render(request, 'job_board/jobs_edit.html', context)


@staff_member_required(login_url='/login/')
def jobs_activate(request, job_id):
    job = get_object_or_404(
              Job, pk=job_id, site_id=get_current_site(request).id
          )
    job.activate()
    return HttpResponseRedirect(job.get_absolute_url())


@login_required(login_url='/login/')
def jobs_expire(request, job_id):
    job = get_object_or_404(
              Job, pk=job_id, site_id=get_current_site(request).id
          )

    if request.user.id != job.user.id:
        return HttpResponseRedirect(job.get_absolute_url())

    job.expire()
    return HttpResponseRedirect(job.get_absolute_url())
