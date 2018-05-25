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
import urllib.request, urllib.error
import json
import socket


# Publicdb setting
PUBLICDB_HOST_FOR_NAGIOS = "http://data.hisparc.nl"

try:
    dirname = os.path.dirname(__file__)
    publicdb_path = os.path.join(dirname, '../..')
    sys.path.append(publicdb_path)

    os.environ['DJANGO_SETTINGS_MODULE'] = 'publicdb.settings'

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
    print(f'Pulseheight {status[1]} - {message}')
    sys.exit(status[0])


def check_pulseheight_mpv(publicdb_host, station_number, plate_number, date):

    publicdb_host = publicdb_host.replace("http://", "")

    try:
        uri = ("http://%s/api/station/%s/plate/%s/pulseheight/fit/%s/%s/%s" %
               (publicdb_host, station_number, plate_number,
                date.year, date.month, date.day))
    except:
        return Nagios.unknown, "Exception raised"

    exit_code = None
    exit_message = None

    timeout = 10

    try:
        response = json.load(urllib.request.urlopen(uri, timeout=timeout))
    except urllib.error.HTTPError:
        exit_code = Nagios.unknown
        exit_message = f'unable to retrieve url: "{uri}"'
    except urllib.error.URLError:
        exit_code = Nagios.critical
        exit_message = f'unable to retrieve url: "{uri}"'
    except socket.timeout:
        exit_code = Nagios.warning
        exit_message = 'timeout in {timeout} seconds trying to retrieve url: "{uri}"'

    if exit_code is not None:
        return exit_code, exit_message

    if "error" in response:
        if j["error"].count("no fit found for plate"):
            return Nagios.ok, response["error"]

        return Nagios.unknown, response["error"]

    return response["nagios"], response["quality"]


if __name__ == '__main__':

    # Check arguments

    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <station number> <plate number>")
        sys.exit(3)

    try:
        station_number = int(sys.argv[1])
        plate_number = int(sys.argv[2])
    except:
        exit(Nagios.unknown,
             "Error in command line arguments, they must all be numbers: "
             "%s, %s, %s, %s" % (sys.argv[1], sys.argv[2]))

    today = datetime.date.today()
    yesterday = today - datetime.timedelta(days=1)

    exit_code, exit_message = check_pulseheight_mpv(PUBLICDB_HOST_FOR_NAGIOS,
                                                    station_number,
                                                    plate_number,
                                                    yesterday)

    exit(exit_code, exit_message)
