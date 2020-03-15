from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import (HttpResponseRedirect, HttpResponsePermanentRedirect,
                         JsonResponse)
from django.shortcuts import get_object_or_404, render

from job_board.forms import CompanyForm
from job_board.models.company import Company
from job_board.models.job import Job


def companies_index(request):
    companies_list = Company.objects \
                            .filter(site_id=get_current_site(request).id)

    for c in companies_list:
        if len(c.paid_jobs()) == 0:
            companies_list = companies_list.exclude(id=c.id)

    paginator = Paginator(companies_list, 25)
    page = request.GET.get('page')
    meta_desc = 'Browse an extensive list of companies with active and ' \
                'expired jobs'
    title = 'Companies'
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        companies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        companies = paginator.page(paginator.num_pages)
    context = {'meta_desc': meta_desc, 'title': title, 'companies': companies}
    return render(request, 'job_board/companies_index.html', context)


@login_required(login_url='/login/')
def companies_new(request):
    title = 'Add a Company'
    site = get_current_site(request)

    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.site_id = site.id
            company.user_id = request.user.id
            company.save()

            if request.is_ajax():
                # NOTE: CockroachDB's id is larger than JavaScript's number
                #       precision (53 bits), which results in the id getting
                #       rounded. Instead, we just convert the id to a string.
                return JsonResponse(
                    {'id': str(company.id), 'name': company.name}
                )
            else:
                messages.success(
                    request,
                    'Your company has been successfully added'
                )
                return HttpResponseRedirect(company.get_absolute_url())

        else:
            if request.is_ajax():
                return render(
                    request,
                    'job_board/_errors.html',
                    {'form': form},
                    status=400
                )
    else:
        form = CompanyForm()

    context = {'form': form, 'title': title}
    return render(request, 'job_board/companies_new.html', context)


def companies_show(request, company_id, slug=None):
    company = get_object_or_404(
                  Company,
                  pk=company_id,
                  site_id=get_current_site(request).id
              )

    if slug is None:
        return HttpResponsePermanentRedirect(company.get_absolute_url())

    # We don't use get_list_or_404 here as we redirect to this view after
    # adding a new company and at that point it won't have any jobs assigned
    # to it.
    jobs = Job.objects.filter(site_id=get_current_site(request).id) \
                      .filter(company=company) \
                      .filter(paid_at__isnull=False) \
                      .order_by('-paid_at')
    title = company.name
    meta_desc = 'Browse a list of all active and expired %s jobs' % \
                company.name
    context = {'meta_desc': meta_desc,
               'title': title,
               'company': company,
               'jobs': jobs}
    return render(request, 'job_board/companies_show.html', context)


@login_required(login_url='/login/')
def companies_edit(request, company_id):
    company = get_object_or_404(
                  Company, pk=company_id, site_id=get_current_site(request).id
              )
    title = 'Edit a Company'

    if (request.user.id != company.user.id) and not request.user.is_staff:
        return HttpResponseRedirect(company.get_absolute_url())

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()

            messages.success(
                request,
                'Your company has been successfully updated'
            )

            return HttpResponseRedirect(company.get_absolute_url())
    else:
        form = CompanyForm(instance=company)

    context = {'company': company, 'form': form, 'title': title}

    return render(request, 'job_board/companies_edit.html', context)
