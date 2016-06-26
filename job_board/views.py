from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import get_list_or_404, get_object_or_404, render
from django.utils import timezone

from .forms import CompanyForm, JobForm
from .models import Category, Company, Job

import markdown


def jobs_index(request):
    jobs = Job.on_site.filter(paid_at__isnull=False).filter(expired_at__isnull=True).order_by('paid_at')
    context = {'jobs': jobs }
    return render(request, 'job_board/jobs_index.html', context)


@login_required(login_url='/login/')
def jobs_mine(request):
    jobs_list = Job.on_site.filter(user_id=request.user.id).order_by('-created_at')
    paginator = Paginator(jobs_list, 25)
    page = request.GET.get('page')
    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        jobs = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        jobs = paginator.page(paginator.num_pages)
    context = {'jobs': jobs }
    return render(request, 'job_board/jobs_mine.html', context)


@login_required(login_url='/login/')
def jobs_new(request):
    if request.method == 'POST':
        form = JobForm(request.POST, initial={'site': '1'})
        if form.is_valid():
            job = form.save(commit=False)
            job.site_id = 1
            job.user_id = request.user.id
            job.save()
            return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))
    else:
        form = JobForm()
    return render(request, 'job_board/jobs_new.html', {'form': form})


def jobs_show(request, job_id):
    job = get_object_or_404(Job, pk=job_id, site_id=request.site)
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

    context = {'job': job, 'post_date': post_date}
    return render(request, 'job_board/jobs_show.html', context)


@login_required(login_url='/login/')
def jobs_edit(request, job_id):
    job = get_object_or_404(Job, pk=job_id, site_id=request.site)

    if request.user.id != job.user.id:
        return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))

    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))
    else:
        form = JobForm(instance=job)

    return render(request, 'job_board/jobs_edit.html', {'form': form, 'job': job})


@staff_member_required(login_url='/login/')
def jobs_activate(request, job_id):
    job = get_object_or_404(Job, pk=job_id, site_id=request.site)
    job.paid_at = timezone.now()
    job.save()
    return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))


@login_required(login_url='/login/')
def jobs_expire(request, job_id):
    job = get_object_or_404(Job, pk=job_id, site_id=request.site)

    if request.user.id != job.user.id:
        return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))

    job.expired_at = timezone.now()
    job.save()
    return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))


@staff_member_required(login_url='/login/')
def jobs_activate(request, job_id):
    job = get_object_or_404(Job, pk=job_id, site_id=request.site)
    job.paid_at = timezone.now()
    job.save()
    return HttpResponseRedirect(reverse('jobs_show', args=(job.id,)))


def categories_index(request):
    categories = Category.on_site.all()
    context = {'categories': categories }
    return render(request, 'job_board/categories_index.html', context)


def categories_show(request, category_id):
    jobs = get_list_or_404(Job, category_id=category_id, site_id=request.site)
    context = {'jobs': jobs}
    return render(request, 'job_board/jobs_index.html', context)


def companies_index(request):
    companies_list = Company.on_site.all()
    paginator = Paginator(companies_list, 25)
    page = request.GET.get('page')
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        companies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        companies = paginator.page(paginator.num_pages)
    context = {'companies': companies }
    return render(request, 'job_board/companies_index.html', context)


@login_required(login_url='/login/')
def companies_new(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST, initial={'site': '1'})
        if form.is_valid():
            company = form.save(commit=False)
            company.site_id = 1
            company.user_id = request.user.id
            company.save()
            return HttpResponseRedirect(reverse('companies_show', args=(company.id,)))
    else:
        form = CompanyForm()
    return render(request, 'job_board/companies_new.html', {'form': form})


def companies_show(request, company_id):
    company = get_object_or_404(Company, pk=company_id, site_id=request.site)
    # We don't use get_list_or_404 here as we redirect to this view after
    # adding a new company and at that point it won't have any jobs assigned
    # to it.
    jobs = Job.on_site.filter(company=company, paid_at__isnull=False).order_by('-paid_at')
    context = {'company': company, 'jobs': jobs}
    return render(request, 'job_board/companies_show.html', context)


@login_required(login_url='/login/')
def companies_edit(request, company_id):
    company = get_object_or_404(Company, pk=company_id, site_id=request.site)

    if request.user.id != company.user.id:
        return HttpResponseRedirect(reverse('companies_show', args=(company.id,)))

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('companies_show', args=(company.id,)))
    else:
        form = CompanyForm(instance=company)
    return render(request, 'job_board/companies_edit.html', {'company': company, 'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse('jobs_index'))
    else:
        form = UserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
