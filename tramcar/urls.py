"""tramcar URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.urls import include, re_path
from django.contrib import admin
from django.contrib.auth import views as auth_views

from job_board.forms import CssAuthenticationForm

urlpatterns = [
    re_path(r'^', include('job_board.urls')),
    re_path(r'^admin/', admin.site.urls),
    # re_path('^', include('django.contrib.auth.urls')),
    re_path(
        r'^login/$',
        auth_views.LoginView.as_view(
            authentication_form=CssAuthenticationForm,
            extra_context={'title': 'Login'}
        ),
        name='login'
    ),
    re_path(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]
