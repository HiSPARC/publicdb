from django.shortcuts import (render_to_response, get_object_or_404,
                              get_list_or_404, redirect)
from django.http import Http404

from ..inforecords.models import Station
from .models import StationLayout, StationLayoutQuarantine

FIRSTDATE = datetime.date(2002, 1, 1)


def submit_layout(request):
    if request.method == 'POST':
        form = QuarantineForm(request.POST)
    else:
        form = QuarantineForm()

    return render_to_response('submit.html',
        {'form': form},
        context_instance=RequestContext(request))


def confirmed_layout(request):
    submitted_layout = get_object_or_404(StationLayoutQuarantine,
                                         hash_submitter=hash,
                                         applicant_verified=False)
    return None


def review_layout(request):
    submitted_layout = get_object_or_404(StationLayoutQuarantine,
                                         hash_reviewer=hash,
                                         applicant_verified=True)
    return None
