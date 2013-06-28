#!/usr/bin/env python

#-------------------------------------------------------------------------------
# Documentation
#
# Based on check_json:
# - https://github.com/HubSpot/HubSpot-Nagios-Plugins/blob/master/check_json
#
# Nagios Plugin API:
# - http://nagios.sourceforge.net/docs/3_0/pluginapi.html
#-------------------------------------------------------------------------------

#-------------------------------------------------------------------------------
# Required packages
#-------------------------------------------------------------------------------

import sys
import datetime

try:
    import urllib2
    import simplejson
    import signal
    from django.conf import settings
except Exception as e:
    print e
    sys.exit(3)

#-------------------------------------------------------------------------------
# Helpers
#-------------------------------------------------------------------------------

class nagios:
    ok = (0, 'OK')
    warning = (1, 'WARNING')
    critical = (2, 'CRITICAL')
    unknown = (3, 'UNKNOWN')

prefix = "Pulseheight"

def exit(status, message):
    print prefix + ' ' + status[1] + ' - ' + message
    sys.exit(status[0])

class TimeoutException(Exception):
    pass

def raise_timeout(signum, frame):
    raise TimeoutException("Timeout was hit.")

signal.signal(signal.SIGALRM, raise_timeout)

#-------------------------------------------------------------------------------
# Main function
#-------------------------------------------------------------------------------

def check_pulseheight_mpv(publicdb_host, stationNumber, plateNumber, date):

    publicdb_host = publicdb_host.replace("http://", "")

    try:
        uri = "http://%s/api/station/%s/plate/%s/pulseheight/fit/%s/%s/%s" % (
            publicdb_host,
            stationNumber, plateNumber,
            date.year, date.month, date.day
        )
    except:
        return nagios.unknown, "Exception raised"

    exit_code = None
    exit_message = None

    try:
        try:
            signal.alarm(10) # raise alarm in X seconds, this is a hack for python 2.5's lack of support for timeout in urlopen :(
            j = simplejson.load(urllib2.urlopen(uri))
        except urllib2.HTTPError, ex:
            exit_code = nagios.unknown
            exit_message = 'unable to retrieve url: "%s"' % uri
        except urllib2.URLError, ex:
            exit_code = nagios.critical
            exit_message = 'unable to retrieve url: "%s"' % uri
        except TimeoutException, ex:
            exit_code = nagios.warning
            exit_message = 'timeout in %s seconds trying to retrieve url: "%s"' % (10, uri)
    finally:
        signal.alarm(0) # disable alarm

    if exit_code is not None:
        return exit_code, exit_message

    #---------------------------------------------------------------------------
    # Evaluate data
    #---------------------------------------------------------------------------

    if "error" in j:
        if j["error"].count("no fit found for plate"):
            return nagios.ok, j["error"]

        return nagios.unknown, j["error"]

    return j["nagios"], j["quality"]

#-------------------------------------------------------------------------------
# Execute from command line
#-------------------------------------------------------------------------------

if __name__ == '__main__':

    # Check arguments

    if len(sys.argv) != 3:
        print "Usage: %s <station number> <plate number>" % sys.argv[0]
        sys.exit(3)

    try:
        stationNumber = int(sys.argv[1])
        plateNumber   = int(sys.argv[2])
    except:
        exit(nagios.unknown, "Error in command line arguments, they must all be numbers: %s, %s, %s, %s" % (
            sys.argv[1],
            sys.argv[2]
        ))

    today = datetime.date.today()
    #today = datetime.date(2011, 5, 1)
    yesterday = today - datetime.timedelta(days=1)

    exit_code, exit_message = check_pulseheight_mpv(
            settings.PUBLICDB_HOST_FOR_NAGIOS,
            stationNumber, plateNumber,
            yesterday)

    exit(exit_code, exit_message)

