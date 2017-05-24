from django.conf.urls import url

import job_board.views.jobs as jobs
import job_board.views.categories as categories
import job_board.views.companies as companies
import job_board.views.misc as misc
import job_board.views.feeds as feeds

urlpatterns = [
    url(r'^$', jobs.jobs_index, name='jobs_index'),
    url(r'^contact/$', misc.contact, name='contact'),
    url(r'^jobs/$', jobs.jobs_index, name='jobs_index'),
    url(r'^jobs/new/$', jobs.jobs_new, name='jobs_new'),
    url(r'^jobs/mine/$', jobs.jobs_mine, name='jobs_mine'),
    url(r'^jobs/(?P<job_id>[0-9]+)/$', jobs.jobs_show, name='jobs_show'),
    url(
        r'^jobs/(?P<job_id>[0-9]+)-(?P<slug>[-\w\d]+)/$',
        jobs.jobs_show,
        name='jobs_show_slug'
    ),
    url(
        r'^jobs/(?P<job_id>[0-9]+)/activate$',
        jobs.jobs_activate,
        name='jobs_activate'
    ),
    url(
        r'^jobs/(?P<job_id>[0-9]+)/expire$',
        jobs.jobs_expire,
        name='jobs_expire'
    ),
    url(r'^jobs/(?P<job_id>[0-9]+)/edit$', jobs.jobs_edit, name='jobs_edit'),
    url(
        r'^categories/$',
        categories.categories_index,
        name='categories_index'
    ),
    url(
        r'^categories/(?P<category_id>[0-9]+)/$',
        categories.categories_show,
        name='categories_show'
    ),
    url(
        r'^categories/(?P<category_id>[0-9]+)-(?P<slug>[-\w\d]+)/$',
        categories.categories_show,
        name='categories_show_slug'
    ),
    url(
        r'^categories/(?P<category_id>[0-9]+)-(?P<slug>[-\w\d]+)/rss$',
        feeds.CategoryFeed(),
        name='categories_feed'
    ),
    url(r'^charge_card$', misc.charge_card, name='charge_card'),
    url(r'^charge_token$', misc.charge_token, name='charge_token'),
    url(r'^companies/$', companies.companies_index, name='companies_index'),
    url(r'^companies/new$', companies.companies_new, name='companies_new'),
    url(
        r'^companies/(?P<company_id>[0-9]+)/$',
        companies.companies_show,
        name='companies_show'
    ),
    url(
        r'^companies/(?P<company_id>[0-9]+)-(?P<slug>[-\w\d]+)/$',
        companies.companies_show,
        name='companies_show_slug'
    ),
    url(
        r'^companies/(?P<company_id>[0-9]+)/edit$',
        companies.companies_edit,
        name='companies_edit'
    ),
    url(r'^register$', misc.register, name='register'),
    url(r'^subscribe$', misc.subscribe, name='subscribe'),
]
