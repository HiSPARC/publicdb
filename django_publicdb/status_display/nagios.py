import urllib2
import re

from django_publicdb.inforecords.models import *


def status_lists():
    """Get various station status lists from Nagios

    :return: down, problem, up. Each of these is a list containing
        station short names that have the status their name implies.

    """
    down = down_list()
    problem = problem_list()
    up = up_list()

    return down, problem, up


def down_list():
    """Get Nagios page which lists DOWN hosts"""

    url = 'http://vpn.hisparc.nl/nagios/cgi-bin/status.cgi?hostgroup=all&style=hostdetail&hoststatustypes=4'
    down_list = retrieve_station_status(url)

    return down_list


def problem_list():
    """Get Nagios page which lists hosts with a problem"""

    url = 'http://vpn.hisparc.nl/nagios/cgi-bin/status.cgi?hostgroup=all&style=detail&servicestatustypes=16&hoststatustypes=2'
    problem_list = retrieve_station_status(url)

    return problem_list


def up_list():
    """Get Nagios page which lists UP hosts"""

    url = 'http://vpn.hisparc.nl/nagios/cgi-bin/status.cgi?hostgroup=all&style=hostdetail&hoststatustypes=2'
    up_list = retrieve_station_status(url)

    return up_list


def retrieve_station_status(url):
    """Get station list from Nagios page which lists hosts of certain level"""

    try:
        req = urllib2.urlopen(url, timeout=2)
        res = req.read()
        station_list = re.findall("host=([a-z0-9]+)\' title", res)
    except urllib2.URLError:
        station_list = []

    return station_list


def get_station_status(station, down, problem, up):
    """Check if station is in down, problem or up list.

    :return: A string denoting the current status of requested station,
        if the station occurs in multiple lists, the worst case is returned.

    """
    try:
        name = Pc.objects.filter(station=station)[0].name
    except IndexError:
        return 'unknown'

    if name in down:
        return 'down'
    elif name in problem:
        return 'problem'
    elif name in up:
        return 'up'
    else:
        return 'unknown'
