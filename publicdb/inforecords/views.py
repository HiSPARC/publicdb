import base64
import socket

from xmlrpc.client import ServerProxy

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render

from .models import Pc, Station


@login_required
def keys(request, host):
    """Return a zip-file containing the hosts OpenVPN keys"""

    host = get_object_or_404(Pc, name=host)

    if settings.VPN_PROXY is not None:
        proxy = ServerProxy(settings.VPN_PROXY)
        key_file = proxy.get_key(host.name, host.type.slug)
        key_file = base64.b64decode(key_file)
    else:
        key_file = 'dummy'

    response = HttpResponse(key_file, content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename={host.name}.zip'
    return response


def create_datastore_config(request):
    """Create the datastore configuration"""

    # Limit access to only allow access from the Datastore server
    if socket.gethostbyaddr(request.META["REMOTE_ADDR"])[0] != settings.DATASTORE_HOST:
        raise PermissionDenied

    return render(
        request,
        'inforecords/datastore.cfg',
        {'stations': Station.objects.all().select_related('cluster__parent')},
        content_type='text/plain',
    )
