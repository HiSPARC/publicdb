from django_publicdb.inforecords.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponse

import xmlrpclib
import base64

from django.conf import settings

def keys(request, host):
    """Return a zip-file containing the hosts OpenVPN keys"""

    host = get_object_or_404(Pc, name=host)

    proxy = xmlrpclib.ServerProxy(settings.VPN_PROXY)
    key_file = proxy.get_key(host.name, host.type.slug)
    key_file = base64.b64decode(key_file)

    response = HttpResponse(key_file, mimetype='application/zip')
    response['Content-Disposition'] = ('attachment; filename=%s.zip' %
                                       host.name)
    return response

def create_nagios_config(request):
    """Create a nagios config file

    This function creates a nagios config file, ready for download.  It
    works by passing a few objects (contacts, clusters and pc's) to a
    template for rendering.  The only logic going on is for the pc's
    services.  First, we don't want to monitor admin pc's.  Secondly, we
    need to pass parameters to the nagios check which are taken from the
    MonitorService model _unless_ they are overridden by the
    EnabledService model.

    """
    # Start building the host list
    hosts = []
    for host in (Pc.objects.exclude(type__description='Admin PC')
                           .filter(is_active=True)):
        services = []
        for service in host.enabledservice_set.all():
            check_command = service.monitor_service.nagios_command
            # Let's see if we need to pass parameters to this service
            if check_command.count('check_nrpe'):
                # The following code will check four variables to see if
                # they exist in the EnabledService instance 'service'.  If
                # they do, assign the value locally using an exec
                # statement.  If they don't, assign a value taken from the
                # MonitorService model associated with the instance.
                for var in ('min_critical', 'max_critical', 'min_warning',
                            'max_warning'):
                    if eval('service.%s' % var):
                        exec('%s = service.%s' % (var, var))
                    else:
                        exec('%s = service.monitor_service.%s' % (var, var))
                # Append the parameters to the check command
                check_command += ('!%s:%s!%s:%s' %
                                 (min_warning, max_warning, min_critical,
                                  max_critical))
            # Append this service to the hosts service list
            services.append(
                {'description': service.monitor_service.description,
                 'check_command': check_command,
		 'active_checks': service.monitor_service.enable_active_checks})
        # Append this host to the hosts list
        hosts.append({'pc': host, 'services': services})

    # Render the template
    return render_to_response('nagios.cfg',
                              {'contacts': Contact.objects.all(),
                               'clusters': Cluster.objects.all(),
                               'hosts': hosts},
                              mimetype='text/plain')

def create_datastore_config(request):
    """Create the datastore configuration"""

    return render_to_response('datastore.cfg',
                              {'stations': Station.objects.all()},
                              mimetype='text/plain')
