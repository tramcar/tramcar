from django.contrib.sites.shortcuts import get_current_site
from django.contrib.syndication.views import Feed
from job_board.models.category import Category
from job_board.models.job import Job

from utils.misc import convert_markdown


class CategoryFeed(Feed):
    def title(self, obj):
        return '%s - %s Jobs Feed' % (obj.site.name, obj.name)

    def link(self, obj):
        return obj.get_absolute_url()

    def description(self, obj):
        return 'The latest %s jobs on %s' % (obj.name, obj.site.name)

    def get_object(self, request, category_id, slug=None):
        return Category.objects.get(
                   pk=category_id, site_id=get_current_site(request).id
               )

    def items(self, obj):
        return Job.objects.filter(category_id=obj) \
                          .filter(paid_at__isnull=False) \
                          .filter(expired_at__isnull=True) \
                          .order_by('-paid_at')[:30]

    def item_title(self, item):
        return '%s @ %s' % (item.title, item.company.name)

    def item_description(self, item):
        return convert_markdown(item.description)
