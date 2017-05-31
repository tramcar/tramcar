from django.contrib.sites.shortcuts import get_current_site
from django.http import HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from job_board.forms import SubscribeForm
from job_board.models.category import Category
from job_board.models.job import Job


def categories_index(request):
    categories = Category.objects.filter(site_id=get_current_site(request).id)

    for c in categories:
        if len(c.active_jobs()) == 0:
            categories = categories.exclude(id=c.id)

    meta_desc = 'Browse a list of all categories with active jobs'
    title = 'Categories'
    context = {'meta_desc': meta_desc,
               'title': title,
               'categories': categories}
    return render(request, 'job_board/categories_index.html', context)


def categories_show(request, category_id, slug=None):
    category = get_object_or_404(
                   Category,
                   pk=category_id,
                   site_id=get_current_site(request).id
    )

    if slug is None:
        return HttpResponsePermanentRedirect(category.get_absolute_url())

    jobs = Job.objects.filter(site_id=get_current_site(request).id) \
                      .filter(category_id=category_id) \
                      .filter(paid_at__isnull=False) \
                      .filter(expired_at__isnull=True) \
                      .order_by('-paid_at')
    form = SubscribeForm()
    meta_desc = 'Browse a list of all active %s jobs' % category.name
    feed_url = reverse('categories_feed', args=(category.id, category.slug(),))
    title = '%s Jobs' % category.name
    context = {'meta_desc': meta_desc,
               'link_rss': feed_url,
               'title': title,
               'form': form,
               'jobs': jobs}
    return render(request, 'job_board/jobs_index.html', context)
