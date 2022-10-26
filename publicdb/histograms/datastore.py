import datetime
import logging
import os
import re

import tables

from django.conf import settings

logger = logging.getLogger(__name__)


def check_for_new_events(last_check_time):
    """Check for new events since last check

    Look for new events written to the datastore since the previous check.

    """
    rootdir = settings.DATASTORE_PATH
    file_list = get_updated_files(rootdir, last_check_time)
    return get_event_summary(file_list)


def get_updated_files(rootdir, last_check_time):
    """Check for updated data files

    Check each file in the datastore and compare its modification
    timestamp to last_check_time.  If the file is newer, return its date
    (from the file name) and path.

    """
    file_list = []
    paths = os.listdir(rootdir)
    for path in paths:
        if re.match('[0-9]+', path):
            path = os.path.join(rootdir, path)
            for dirpath, _, filenames in os.walk(path):
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    mtime = os.path.getmtime(file_path)
                    if mtime >= last_check_time:
                        try:
                            date = datetime.datetime.strptime(file, '%Y_%m_%d.h5').date()
                        except ValueError:
                            continue
                        if date != datetime.datetime.utcnow().date() and date != datetime.datetime.today():
                            file_list.append((date, file_path))

    return file_list


def get_event_summary(file_list):
    """Summarize event numbers per station

    :param file_list: list of tuples containing a date and file path.

    :return: the number of events per station for each event type for
        each file in file_list. This info is compiled in a dictionary:
        {'[date]': {'[station_number]': {'[table_name]': [n_rows], }, }, }


    """
    summary = {}
    for date, file in file_list:
        stations = {}
        with tables.open_file(file, 'r') as data:
            for cluster in data.list_nodes('/hisparc'):
                for station in data.list_nodes(cluster):
                    num = int(re.search('([0-9]+)$', station._v_name).group())
                    event_tables = {}
                    for table in data.list_nodes(station):
                        event_tables[table.name] = len(table)
                    stations[num] = event_tables
        summary[date] = stations

    return summary


def get_stations(date):
    """Get all stations with data on specified date

    Return a list of stations which have data on the specified date by
    accessing the data file.

    :param date: the date to check for

    :return: a list of stations

    """
    path = get_data_path(date)

    station_list = []
    with tables.open_file(path, 'r') as file:
        for cluster in file.list_nodes('/hisparc'):
            for station in file.list_nodes(cluster):
                match = re.match('station_(?P<station>[0-9]+)', station._v_name)
                station_list.append(int(match.group('station')))

    return station_list


def get_data_path(date):
    """Return path to data file

    Return path to the data file of a particular date

    :param date: the date as a datetime.date object

    :return: path to the data file

    """
    rootdir = settings.DATASTORE_PATH
    filepath = date.strftime('%Y/%-m/%Y_%-m_%-d.h5')
    return os.path.join(rootdir, filepath)


def get_config_messages(cluster, station_number, date):
    """Get configuration messages

    :param cluster: string containing the cluster name
    :param station_number: station number
    :param date: date

    """
    path = get_data_path(date)

    file = tables.open_file(path, 'r')
    parent = file.get_node(f'/hisparc/cluster_{cluster.lower()}/station_{station_number}')
    config = file.get_node(parent, 'config')
    blobs = file.get_node(parent, 'blobs')
    return file, config, blobs
