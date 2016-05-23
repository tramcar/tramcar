from django.contrib import admin

from .models import Category, Company, Country, Job

admin.site.register(Category)
admin.site.register(Company)
admin.site.register(Country)
admin.site.register(Job)

# Register your models here.
