from django.http import HttpResponse
from controlpanel.inforecords.models import *
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

        # Het aanmaken van nagios config
        
        # Om te beginnen met de clusters defineren
        clusters = Cluster.objects.all()
        clusterinfo = u''
        for clus in clusters:
                clusterinfo += u'define hostgroup{\n    hostgroup_name  cluster%s\n     alias   %s\n}\n\n' % (clus.id, clus.name)

        # Nu de contacten defineren
        contacten = Contact.objects.all()
        contactinfo = u''
        for cont in contacten:
                contactinfo += u'define contact{\n      contact_name    contact%s\n     alias   %s\n    host_notifications_enabled      1\n     service_notifications_enabled   1\n     service_notification_period     24x7\n  host_notification_period        24x7\n  service_notification_options    w,u,c,r\n       host_notification_options       d,u,r\n service_notification_commands   notify-service-by-email\n       host_notification_commands      notify-host-by-email\n  email   %s\n}\n\n' % (cont.id, cont, cont.email)


        #Nu de machines zelf defineren
        machines = Pc.objects.exclude(type='7')
        machineinfo = u''
        for mach in machines:

                if not mach.station.contact_id:
                        machcontact = u'contact84'
                else:
                        machcontact = u'contact%s' % (mach.station.contact_id)
                machineinfo += u'define host{\n host_name       %s\n    alias   %s\n    address %s\n    hostgroups      cluster%s\n     check_command   check-host-alive\n      check_interval  30\n    retry_interval  10\n    max_check_attempts      5\n     check_period    24x7\n  process_perf_data       0\n     retain_nonstatus_information    0\n     contacts        %s\n    notification_interval   10080\n notification_period     24x7\n  notification_options    d,u,r\n}\n\n' % (mach.name, mach.name,mach.ip,mach.station.cluster().id,machcontact)

                # Nu de bijbehorende monitor diensten ophalen
                services =  EnabledService.objects.filter(pc=mach)
                for serv in services:
                        if serv.monitor_service.nagios_command.split('!')[0] == 'check_nrpe':
                                # kijken of er overrides zijn gedaan op de standaard waardes
                                if serv.min_warning:
                                        minwarning = serv.min_warning
                                else:
                                        minwarning = serv.monitor_service.min_warning
                                if serv.max_warning:
                                        maxwarning = serv.max_warning
                                else:
                                        maxwarning = serv.monitor_service.max_warning
                                if serv.min_critical:
                                        mincritical = serv.min_critical
                                else:
                                        mincritical = serv.monitor_service.min_critical
                                if serv.max_critical:
                                        maxcritical = serv.max_critical
                                else:
                                        maxcritical = serv.monitor_service.max_critical

                                nagios_command = u'%s!%s:%s!%s:%s' % (serv.monitor_service.nagios_command,minwarning,maxwarning,mincritical,maxcritical)
                        else:
                                nagios_command = serv.monitor_service.nagios_command
                        machineinfo += u'define service{\n      use generic-service\n   host_name       %s\n    service_description     %s\n    check_command   %s\n    notification_interval   10080\n}\n\n' % (mach.name,serv.monitor_service.description,nagios_command)

        # Het wegschrijven van de configuratie file, latin-1 wordt gedaan om de wazige tekens boven de e te kunnen wegschrijven
        nagiosconfig = open('/usr/local/nagios/etc/objects/hisparc.cfg','w')
        nagiosconfig.write(clusterinfo.encode('latin-1'))
        nagiosconfig.write(contactinfo.encode('latin-1'))
        nagiosconfig.write(machineinfo.encode('latin-1'))
        nagiosconfig.close()
        # Het restarten van nagios, dnsmasq en openvpn om de nagios en dns configuratie door te voeren
        restartnagios = os.popen("sudo /etc/init.d/nagios stop && sudo /etc/init.d/nagios start && sudo /etc/init.d/dnsmasq condrestart && sudo /etc/init.d/openvpn restart")
        return HttpResponse(restartnagios)
