from django.contrib.sites.shortcuts import get_current_site
from job_board.forms import SearchForm


def search_form(request):
    return {'search_form': SearchForm()}


def get_site(request):
    return {'current_site': get_current_site(request)}
