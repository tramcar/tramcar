from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404, render

from job_board.models.category import Category
from job_board.models.job import Job


def categories_index(request):
    categories = Category.objects.filter(site_id=get_current_site(request).id)
    title = 'Categories'
    context = {'categories': categories, 'title': title}
    return render(request, 'job_board/categories_index.html', context)


def categories_show(request, category_id):
    category = get_object_or_404(
                   Category,
                   pk=category_id,
                   site_id=get_current_site(request).id
    )

    jobs = Job.objects.filter(site_id=get_current_site(request).id) \
                      .filter(category_id=category_id) \
                      .filter(paid_at__isnull=False) \
                      .filter(expired_at__isnull=True) \
                      .order_by('-paid_at')
    context = {'jobs': jobs, 'title': '%s Jobs' % category.name}
    return render(request, 'job_board/jobs_index.html', context)
