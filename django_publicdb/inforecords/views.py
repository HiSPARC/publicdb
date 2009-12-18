from django.http import HttpResponse
from django_publicdb.inforecords.models import *
from django.shortcuts import render_to_response
import os
import tempfile
import zipfile
import StringIO

locatiecertificaat = '/etc/openvpn/keys'
locatiecertificaatadmin = '/etc/openvpn/adminkeys'
locatieopenssl = '/etc/openvpn/openssl.cnf'
locatieopenssladmin = '/etc/openvpn/openssladmin.cnf'

def indexpagina(request):
        return HttpResponse("Welkom bij vpn.hisparc.nl")        

# Voor het bouwen van certificaten die nog niet bestaan
def bouwcertificaat(key_config,key_dir,machineid,ipadres):
        os.popen((('export KEY_CONFIG=%s && export KEY_DIR=%s && cd $KEY_DIR && export KEY_SIZE=2048 && export KEY_COUNTRY=NL && export KEY_PROVINCE=NH && export KEY_CITY=Amsterdam && export KEY_ORG="HiSPARC, Nikhef" && export KEY_EMAIL="hisparc@nikhef.nl" && export COMMON_NAME="%s" && openssl req -days 3650 -nodes -new -keyout $COMMON_NAME.key -out $COMMON_NAME.csr -batch -config $KEY_CONFIG && openssl ca -days 3650 -out $COMMON_NAME.crt -in $COMMON_NAME.csr -batch -config $KEY_CONFIG') % (key_config,key_dir,machineid)))
        
        # voor de ip adres te configureren
        if not ipadres == '1':
                ipfile=open(('/etc/openvpn/ccd/%s' % (machineid)), 'w')
                ipfile.write(('ifconfig-push %s 255.255.254.0 194.171.82.1') % (ipadres))
                ipfile.close()
                # Om de dns reacord aan te maken
                dnsfile=open('/etc/hosts', 'a')
                dnsfile.write(('\n%s    %s.his') % (ipadres,machineid))
                dnsfile.close()
        return 1

# Voor het generen van zip files
def genereer(request,sleutel,machineid):

    if not request.user.is_authenticated():
      return HttpResponse('Dat mag niet!')

    if not Pc.objects.filter(name=machineid,type=sleutel):
      return HttpResponse('De VPN PC bestaat niet!')

    if sleutel == '7':
      locatie = locatiecertificaatadmin
      openssl = locatieopenssladmin
    else:
      locatie = locatiecertificaat
      openssl = locatieopenssl



    # bestaat de benodige certificaten?
    if not os.path.exists('%s/%s.crt' % (locatie,machineid)):
        if sleutel == '7':
           ipadres = '1'
        else:
           ipadres = Pc.objects.filter(name=machineid)[0].ip
        bouwcertificaat(openssl,locatie,machineid,ipadres)
        #return HttpResponse(loldielol)
    # De certificaten bestaan dus we gaan ze openen om ze te kunnen uitlezen
    tempcrt = open('%s/%s.crt' % (locatie,machineid))
    tempkey = open('%s/%s.key' % (locatie,machineid))
    ta = open('%s/ta.key' % (locatiecertificaat))
    ca = open('%s/ca.crt' % (locatie))

    # Om ruimte te maken waarin je zipjes kan maken
    output = StringIO.StringIO()

    # Voor het bouwen van het zipje zelf.
    zip = zipfile.ZipFile(output, 'a')
    if sleutel == '7':
        zip.writestr('hisparc_admin.crt',tempcrt.read())
        zip.writestr('hisparc_admin.key',tempkey.read())
        zip.writestr('ca_admin.crt',ca.read())
    else:
        zip.writestr('hisparc.crt',tempcrt.read())
        zip.writestr('hisparc.key',tempkey.read())
        zip.writestr('ca.crt',ca.read())
    zip.writestr('ta.key',ta.read())
    zip.close()

    return HttpResponse( content=output.getvalue(), mimetype='application/zip')


# Het genereren van Configuratie files voor Nagios en DNS
def maakconfig(request):
        if not request.user.is_authenticated():
              return HttpResponse('Dat mag niet!')

	pipe = os.popen("wget http://vpn.hisparc.nl/django/config/nagios -O /usr/local/nagios/etc/objects/hisparc.cfg")
	output = pipe.readlines()
	pipe.close()
        pipe = os.popen("sudo /etc/init.d/nagios force-reload")
	output += pipe.readlines()
	pipe.close()
        pipe = os.popen("sudo /etc/init.d/dnsmasq reload")
	output += pipe.readlines()
	pipe.close()
	pipe = os.popen("sudo /etc/init.d/openvpn reload")
	output += pipe.readlines()
	pipe.close()
        return HttpResponse(output)

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
