from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^$', views.jobs_index, name='jobs_index'),
    url(r'^jobs/$', views.jobs_index, name='jobs_index'),
    url(r'^jobs/new/$', views.jobs_new, name='jobs_new'),
    url(r'^jobs/mine/$', views.jobs_mine, name='jobs_mine'),
    url(r'^jobs/(?P<job_id>[0-9]+)/$', views.jobs_show, name='jobs_show'),
    url(r'^jobs/(?P<job_id>[0-9]+)/activate$', views.jobs_activate, name='jobs_activate'),
    url(r'^jobs/(?P<job_id>[0-9]+)/expire$', views.jobs_expire, name='jobs_expire'),
    url(r'^jobs/(?P<job_id>[0-9]+)/edit$', views.jobs_edit, name='jobs_edit'),
    url(r'^categories/$', views.categories_index, name='categories_index'),
    url(r'^categories/(?P<category_id>[0-9]+)/$', views.categories_show, name='categories_show'),
    url(r'^companies/$', views.companies_index, name='companies_index'),
    url(r'^companies/new$', views.companies_new, name='companies_new'),
    url(r'^companies/(?P<company_id>[0-9]+)/$', views.companies_show, name='companies_show'),
    url(r'^companies/(?P<company_id>[0-9]+)/edit$', views.companies_edit, name='companies_edit'),
    url(r'^register$', views.register, name='register'),
]
