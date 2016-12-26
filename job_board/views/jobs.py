from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string

from utils.misc import send_mail_with_helper

from job_board.forms import JobForm, JobRemoteForm
from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.job import Job

import markdown


def jobs_index(request):
    jobs = Job.objects.filter(site_id=get_current_site(request).id) \
                      .filter(paid_at__isnull=False) \
                      .filter(expired_at__isnull=True) \
                      .order_by('-paid_at')[:10]
    title = 'Latest Jobs'
    context = {'jobs': jobs, 'title': title}
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

    if request.method == 'POST':
        if site.siteconfig.remote:
            form = JobRemoteForm(request.POST)
        else:
            form = JobForm(request.POST)

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

            messages.success(request, 'Your job has been successfully added')

            return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))
    else:
        if site.siteconfig.remote:
            form = JobRemoteForm()
        else:
            form = JobForm()

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
               'title': title,
               'protocol': site.siteconfig.protocol}
    return render(request, 'job_board/jobs_new.html', context)


def jobs_show(request, job_id):
    job = get_object_or_404(
              Job, pk=job_id, site_id=get_current_site(request).id
          )
    site = get_current_site(request)
    # If the browsing user does not own the job, and the job has yet to be paid
    # for, then 404
    if job.user_id != request.user.id and job.paid_at is None:
        raise Http404("No Job matches the given query.")
    # If the browsing user owns the job, and the job is unpaid for, display the
    # job's created_at date instead of paid_at
    if job.user_id == request.user.id and job.paid_at is None:
        post_date = job.created_at
    else:
        post_date = job.paid_at
    md = markdown.Markdown(safe_mode='remove')
    job.description_md = md.convert(job.description)
    job.application_info_md = md.convert(job.application_info)
    job.remote = "Yes" if job.remote else "No"
    title = "%s @ %s" % (job.title, job.company.name)
    stripe_key = site.siteconfig.stripe_publishable_key

    context = {'job': job,
               'post_date': post_date,
               'title': title,
               'remote': site.siteconfig.remote,
               'stripe_publishable_key': stripe_key,
               'price': site.siteconfig.price,
               'price_in_cents': site.siteconfig.price_in_cents()}
    return render(request, 'job_board/jobs_show.html', context)


@login_required(login_url='/login/')
def jobs_edit(request, job_id):
    site = get_current_site(request)
    protocol = site.siteconfig.protocol
    job = get_object_or_404(
              Job, pk=job_id, site_id=site.id
          )
    title = 'Edit a Job'

    if request.user.id != job.user.id:
        return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))

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

            return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))
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
    return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))


@login_required(login_url='/login/')
def jobs_expire(request, job_id):
    job = get_object_or_404(
              Job, pk=job_id, site_id=get_current_site(request).id
          )

    if request.user.id != job.user.id:
        return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))

    job.expire()
    return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))
