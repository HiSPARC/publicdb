#!/usr/bin/env python

""" Check Pulseheight MPV Nagios plugin

Based on check_json:
- https://github.com/HubSpot/HubSpot-Nagios-Plugins/blob/master/check_json

Nagios Plugin API:
- http://nagios.sourceforge.net/docs/3_0/pluginapi.html

"""
import sys
import datetime
import os
import urllib2
import json
import signal
import socket


# Publicdb setting
PUBLICDB_HOST_FOR_NAGIOS = "http://data.hisparc.nl"

try:
    dirname = os.path.dirname(__file__)
    publicdb_path = os.path.join(dirname, '../..')
    sys.path.append(publicdb_path)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'django_publicdb.settings'

    from django.conf import settings

    PUBLICDB_HOST_FOR_NAGIOS = settings.PUBLICDB_HOST_FOR_NAGIOS
except:
    pass


class Nagios:
    ok = (0, 'OK')
    warning = (1, 'WARNING')
    critical = (2, 'CRITICAL')
    unknown = (3, 'UNKNOWN')


def exit(status, message):
    print 'Pulseheight ' + status[1] + ' - ' + message
    sys.exit(status[0])


def check_pulseheight_mpv(publicdb_host, stationNumber, plateNumber, date):

    publicdb_host = publicdb_host.replace("http://", "")

    try:
        uri = "http://%s/api/station/%s/plate/%s/pulseheight/fit/%s/%s/%s" % (
                publicdb_host, stationNumber, plateNumber,
                date.year, date.month, date.day)
    except:
        return Nagios.unknown, "Exception raised"

    exit_code = None
    exit_message = None

    timeout = 10

    try:
        j = json.load(urllib2.urlopen(uri, timeout=timeout))
    except urllib2.HTTPError, ex:
        exit_code = Nagios.unknown
        exit_message = 'unable to retrieve url: "%s"' % uri
    except urllib2.URLError, ex:
        exit_code = Nagios.critical
        exit_message = 'unable to retrieve url: "%s"' % uri
    except socket.timeout, ex:
        exit_code = Nagios.warning
        exit_message = 'timeout in %d seconds trying to retrieve url: "%s"' % (
                            timeout, uri)

    if exit_code is not None:
        return exit_code, exit_message

    if "error" in j:
        if j["error"].count("no fit found for plate"):
            return Nagios.ok, j["error"]

        return Nagios.unknown, j["error"]

    return j["nagios"], j["quality"]


if __name__ == '__main__':

    # Check arguments

    if len(sys.argv) != 3:
        print "Usage: %s <station number> <plate number>" % sys.argv[0]
        sys.exit(3)

    try:
        stationNumber = int(sys.argv[1])
        plateNumber = int(sys.argv[2])
    except:
        exit(Nagios.unknown,
             "Error in command line arguments, they must all be numbers: "
             "%s, %s, %s, %s" % (sys.argv[1], sys.argv[2]))

    today = datetime.date.today()
    #today = datetime.date(2011, 5, 1)
    yesterday = today - datetime.timedelta(days=1)

    exit_code, exit_message = check_pulseheight_mpv(PUBLICDB_HOST_FOR_NAGIOS,
                                                    stationNumber,
                                                    plateNumber,
                                                    yesterday)

    exit(exit_code, exit_message)
