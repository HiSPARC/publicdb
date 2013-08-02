import urllib2
import socket
import re

from django_publicdb.inforecords.models import *


def status_lists():
    """Get various station status lists from Nagios

    :return: down, problem, up. lists containing station short names that have
             the status the variable name implies.

    """
    down = down_list()
    problem = problem_list()
    up = up_list()

    return down, problem, up


def down_list():
    """Get Nagios page which lists DOWN hosts

    :return: list of station short names of stations that are DOWN.

    """
    query = 'hostgroup=all&style=hostdetail&hoststatustypes=4'
    down = retrieve_station_status(query)

    return down


def problem_list():
    """Get Nagios page which lists hosts with a problem

    :return: list containing station short names of stations for which
             the host has status OK, but some services are CRITICAL.

    """
    query = 'hostgroup=all&style=detail&servicestatustypes=16&hoststatustypes=2'
    problem = retrieve_station_status(query)

    return problem


def up_list():
    """Get Nagios page which lists UP hosts

    :return: list of station short names of stations that are OK.

    """
    query = 'hostgroup=all&style=hostdetail&hoststatustypes=2'
    up = retrieve_station_status(query)

    return up


def retrieve_station_status(query):
    """Get station list from Nagios page which lists hosts of certain level

    :param query: query to filter stations on Nagios.

    :return: list of station short names on the given page.

    """
    nagios_base = "http://vpn.hisparc.nl/cgi-bin/status.cgi?"

    try:
        req = urllib2.urlopen(nagios_base + query, timeout=1)
        res = req.read()
        stations = re.findall("host=([a-z0-9]+)\' title", res)
    except (urllib2.URLError, socket.timeout):
        stations = []

    return stations


def get_station_status(station, down, problem, up):
    """Check if station is in down, problem or up list.

    :param station: station_id for which you want the status.
    :param down: list of stations that are DOWN.
    :param problem: list of stations that have a service CRITICAL (but are UP).
    :param up: list of stations that are UP.
    :return: string denoting the current status of requested station, if the
             station occurs in multiple lists, the worst case is returned.

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

def get_status_counts(down, problem, up):
    """
    :param down: list of stations that are DOWN.
    :param problem: list of stations that have a service CRITICAL (but are UP).
    :param up: list of stations that are UP.
    :return: dictionary containing the counts of stations with a status.

    """
    statuscount = {'up': len(up), 'problem': len(problem), 'down': len(down)}
    return statuscount
