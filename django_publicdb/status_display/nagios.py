import urllib2
import socket
import re

from django_publicdb.inforecords.models import Station


def status_lists():
    """Get various station status lists from Nagios

    :return: down, problem, up. lists containing station short names that have
             the status the variable name implies.

    """
    down = down_list()
    problem = problem_list()
    up = up_list().difference(problem)

    return down, problem, up


def down_list():
    """Get Nagios page which lists DOWN hosts

    :return: set of station number of stations that are DOWN.

    """
    query = 'hostgroup=all&style=hostdetail&hoststatustypes=4'
    down = retrieve_station_status(query)
    down_numbers = pc_name_to_station_number(down)

    return set(down_numbers)


def problem_list():
    """Get Nagios page which lists hosts with a problem

    :return: set containing station number of stations for which
             the host has status OK, but some services are CRITICAL.

    """
    query = ('hostgroup=all&style=detail&servicestatustypes=16&'
             'hoststatustypes=2')
    problem = retrieve_station_status(query)
    problem_numbers = pc_name_to_station_number(problem)

    return set(problem_numbers)


def up_list():
    """Get Nagios page which lists UP hosts

    :return: set of station numbers of stations that are OK.

    """
    query = 'hostgroup=all&style=hostdetail&hoststatustypes=2'
    up = retrieve_station_status(query)
    up_numbers = pc_name_to_station_number(up)

    return set(up_numbers)


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


def pc_name_to_station_number(shortnames):
    """Convert list of pc names to station numbers

    :param shortnames: list of pc names.

    :return: station numbers that have a pc with name in the shortnames.

    """
    stations = list(Station.objects.filter(pc__name__in=shortnames)
                                   .values_list('number', flat=True))
    return stations


def get_station_status(station_number, down, problem, up):
    """Check if station is in down, problem or up list.

    :param station_number: station for which you want the status.
    :param down: list of stations that are DOWN.
    :param problem: list of stations that have a service CRITICAL (but are UP).
    :param up: list of stations that are UP.

    :return: string denoting the current status of requested station, if the
             station occurs in multiple lists, the worst case is returned.

    """
    if station_number in down:
        return 'down'
    elif station_number in problem:
        return 'problem'
    elif station_number in up:
        return 'up'
    else:
        return 'unknown'


def get_status_counts(down, problem, up):
    """Get the lengths of the status lists

    :param down: set of stations that are DOWN.
    :param problem: set of stations that have a service CRITICAL (but are UP).
    :param up: set of stations that are UP and have no services CRITICAL.
    :return: dictionary containing the counts of stations with a status.

    """
    statuscount = {'down': len(down), 'problem': len(problem), 'up': len(up)}
    return statuscount
