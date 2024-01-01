from django.urls import re_path

import job_board.views.jobs as jobs
import job_board.views.categories as categories
import job_board.views.companies as companies
import job_board.views.misc as misc
import job_board.views.feeds as feeds

urlpatterns = [
    re_path(r'^$', jobs.jobs_index, name='jobs_index'),
    re_path(r'^contact/$', misc.contact, name='contact'),
    re_path(r'^jobs/$', jobs.jobs_index, name='jobs_index'),
    re_path(r'^jobs/new/$', jobs.jobs_new, name='jobs_new'),
    re_path(r'^jobs/search/$', jobs.jobs_search, name='jobs_search'),
    re_path(r'^jobs/mine/$', jobs.jobs_mine, name='jobs_mine'),
    re_path(r'^jobs/(?P<job_id>[0-9]+)/$', jobs.jobs_show, name='jobs_show'),
    re_path(
        r'^jobs/(?P<job_id>[0-9]+)-(?P<slug>[-\w\d]+)/$',
        jobs.jobs_show,
        name='jobs_show_slug'
    ),
    re_path(
        r'^jobs/(?P<job_id>[0-9]+)/activate$',
        jobs.jobs_activate,
        name='jobs_activate'
    ),
    re_path(
        r'^jobs/(?P<job_id>[0-9]+)/expire$',
        jobs.jobs_expire,
        name='jobs_expire'
    ),
    re_path(
        r'^jobs/(?P<job_id>[0-9]+)/edit$',
        jobs.jobs_edit,
        name='jobs_edit'
    ),
    re_path(
        r'^categories/$',
        categories.categories_index,
        name='categories_index'
    ),
    re_path(
        r'^categories/(?P<category_id>[0-9]+)/$',
        categories.categories_show,
        name='categories_show'
    ),
    re_path(
        r'^categories/(?P<category_id>[0-9]+)-(?P<slug>[-\w\d]+)/$',
        categories.categories_show,
        name='categories_show_slug'
    ),
    re_path(
        r'^categories/(?P<category_id>[0-9]+)-(?P<slug>[-\w\d]+)/rss$',
        feeds.CategoryFeed(),
        name='categories_feed'
    ),
    re_path(r'^charge_card$', misc.charge_card, name='charge_card'),
    re_path(r'^charge_token$', misc.charge_token, name='charge_token'),
    re_path(
        r'^companies/$',
        companies.companies_index,
        name='companies_index'
    ),
    re_path(r'^companies/new$', companies.companies_new, name='companies_new'),
    re_path(
        r'^companies/(?P<company_id>[0-9]+)/$',
        companies.companies_show,
        name='companies_show'
    ),
    re_path(
        r'^companies/(?P<company_id>[0-9]+)-(?P<slug>[-\w\d]+)/$',
        companies.companies_show,
        name='companies_show_slug'
    ),
    re_path(
        r'^companies/(?P<company_id>[0-9]+)/edit$',
        companies.companies_edit,
        name='companies_edit'
    ),
    re_path(r'^register$', misc.register, name='register'),
    re_path(r'^subscribe$', misc.subscribe, name='subscribe'),
]
