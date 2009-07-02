from django.shortcuts import render_to_response
from jobs import *

def update_check(request):
    check_for_updates()
    return render_to_response('histograms/update_check.html')

def update_histograms(request):
    update_all_histograms()
    return render_to_response('histograms/update_histograms.html')
