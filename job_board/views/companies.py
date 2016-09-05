from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render

from job_board.forms import CompanyForm
from job_board.models.company import Company
from job_board.models.job import Job


def companies_index(request):
    companies_list = Company.objects \
                            .filter(site_id=get_current_site(request).id)
    paginator = Paginator(companies_list, 25)
    page = request.GET.get('page')
    title = 'Companies'
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        companies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        companies = paginator.page(paginator.num_pages)
    context = {'companies': companies, 'title': title}
    return render(request, 'job_board/companies_index.html', context)


@login_required(login_url='/login/')
def companies_new(request):
    title = 'Add a Company'
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            company = form.save(commit=False)
            company.site_id = get_current_site(request).id
            company.user_id = request.user.id
            company.save()
            return HttpResponseRedirect(reverse('companies_show',
                                                args=(company.id,)))
    else:
        form = CompanyForm()
    context = {'form': form, 'title': title}
    return render(request, 'job_board/companies_new.html', context)


def companies_show(request, company_id):
    company = get_object_or_404(
                  Company,
                  pk=company_id,
                  site_id=get_current_site(request).id
              )
    # We don't use get_list_or_404 here as we redirect to this view after
    # adding a new company and at that point it won't have any jobs assigned
    # to it.
    jobs = Job.objects.filter(site_id=get_current_site(request).id) \
                      .filter(company=company) \
                      .filter(paid_at__isnull=False) \
                      .order_by('-paid_at')
    title = company.name
    context = {'company': company, 'jobs': jobs, 'title': title}
    return render(request, 'job_board/companies_show.html', context)


@login_required(login_url='/login/')
def companies_edit(request, company_id):
    company = get_object_or_404(
                  Company, pk=company_id, site_id=get_current_site(request).id
              )
    title = 'Edit a Company'

    if request.user.id != company.user.id:
        return HttpResponseRedirect(reverse('companies_show',
                                            args=(company.id,)))

    if request.method == 'POST':
        form = CompanyForm(request.POST, instance=company)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect(reverse('companies_show',
                                                args=(company.id,)))
    else:
        form = CompanyForm(instance=company)

    context = {'company': company, 'form': form, 'title': title}

    return render(request, 'job_board/companies_edit.html', context)
