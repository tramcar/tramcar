from django.contrib import admin

from .models import Category, Company, Country, Job, SiteConfig

admin.site.register(Category)
admin.site.register(Company)
admin.site.register(Country)
admin.site.register(Job)
admin.site.register(SiteConfig)

# Register your models here.
