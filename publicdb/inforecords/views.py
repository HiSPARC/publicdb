from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.shortcuts import render

from .models import Station


def create_datastore_config(request):
    """Create the datastore configuration"""

    # Limit access to only allow access from the Datastore server
    if request.META['REMOTE_HOST'] != settings.DATASTORE_HOST:
        raise PermissionDenied

    return render(
        request,
        'inforecords/datastore.cfg',
        {'stations': Station.objects.all().select_related('cluster__parent')},
        content_type='text/plain',
    )
