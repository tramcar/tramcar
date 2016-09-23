from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render

from job_board.forms import CssUserCreationForm


def register(request):
    if request.method == 'POST':
        form = CssUserCreationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            return HttpResponseRedirect(reverse('jobs_index'))
    else:
        form = CssUserCreationForm()
    return render(request, "registration/register.html", {
        'form': form,
    })
