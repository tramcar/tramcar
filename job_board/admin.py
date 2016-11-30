from django.contrib import admin

from job_board.forms import SiteConfigForm
from job_board.models.category import Category
from job_board.models.company import Company
from job_board.models.country import Country
from job_board.models.job import Job
from job_board.models.site_config import SiteConfig


class SiteConfigAdmin(admin.ModelAdmin):
    form = SiteConfigForm


# Register your models here.
admin.site.register(Category)
admin.site.register(Company)
admin.site.register(Country)
admin.site.register(Job)
admin.site.register(SiteConfig, SiteConfigAdmin)
