from django.shortcuts import render_to_response
from django.template import RequestContext


def index(request):
    """Show the static index page"""
    return render_to_response('index.html',
                              context_instance=RequestContext(request))
