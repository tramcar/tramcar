from django.contrib.sites.shortcuts import get_current_site


def get_site(request):
    return {'current_site': get_current_site(request)}
