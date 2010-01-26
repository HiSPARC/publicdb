import os
import re
import datetime
import tables

from django.conf import settings

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
    timestamp to last_check_time.  If the file is newer, return its path.

    """
    file_list = []
    paths = os.listdir(rootdir)
    for path in paths:
        if re.match('[0-9]+', path):
            path = os.path.join(rootdir, path)
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    file_path = os.path.join(dirpath, file)
                    mtime = os.path.getmtime(file_path)
                    if mtime > last_check_time:
                        date = datetime.datetime.strptime(
                                    file, '%Y_%m_%d.h5').date()
                        if date != datetime.date.today():
                            file_list.append((date, file_path))

    return file_list

def get_event_summary(file_list):
    """Summarize event numbers per station

    For each file in file_list, return the number of events per station
    for each event type

    """
    summary = {}
    for date, file in file_list:
        stations = {}
        with tables.openFile(file, 'r') as data:
            for cluster in data.listNodes('/hisparc'):
                for station in data.listNodes(cluster):
                    num = int(re.search('([0-9]+)$',
                              station._v_name).group())
                    event_tables = {}
                    for table in data.listNodes(station):
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
    with tables.openFile(path) as file:
        for cluster in file.listNodes('/hisparc'):
            for station in file.listNodes(cluster):
                m = re.match('station_(?P<station>[0-9]+)',
                             station._v_name)
                station_list.append(int(m.group('station')))

    return station_list

def get_event_timestamps(cluster, station_id, date):
    """Get event timestamps

    Read data from file and return a list of timestamps for all events on
    date `date' from station `station_id'.

    :param cluster: string containing the cluster name
    :param station_id: station number
    :param date: date

    """
    return get_event_data(cluster, station_id, date, 'timestamp')

def get_pulseheights(cluster, station_id, date):
    """Get all event pulse heights

    Read data from file and return a list of pulseheights.

    :param cluster: string containing the cluster name
    :param station_id: station number
    :param date: date

    """
    pulseheights = get_event_data(cluster, station_id, date,
                                  'pulseheights')
    if pulseheights is None:
        return None
    else:
        #FIXME
        # need configurations for this
        pulseheights = [[x * .57 for x in y] for y in pulseheights]

        # transpose, so we have 4 arrays of many pulseheights
        return zip(*pulseheights)

def get_integrals(cluster, station_id, date):
    """Get all event integrals

    Read data from file and return a list of integrals.

    :param cluster: string containing the cluster name
    :param station_id: station number
    :param date: date

    """
    integrals = get_event_data(cluster, station_id, date, 'integrals')
    if integrals is None:
        return None
    else:
        #FIXME
        # need configurations for this
        integrals = [[x * .57 for x in y] for y in integrals]

        # transpose, so we have 4 arrays of many integrals
        return zip(*integrals)

def get_event_data(cluster, station_id, date, quantity):
    """Get event data of a specific quantity

    :param cluster: string containing the cluster name
    :param station_id: station number
    :param date: date
    :param quantity: the specific event data type

    """
    path = get_data_path(date)

    with tables.openFile(path) as file:
        parent = file.getNode('/hisparc/cluster_%s/station_%d' %
                              (cluster.lower(), station_id))
        try:
            data = [x[quantity] for x in parent.events]
        except tables.NoSuchNodeError:
            data = None

    return data

def get_data_path(date):
    """Return path to data file

    Return path to the data file of a particular date

    :param date: the date

    :return: path to the data file

    """
    rootdir = settings.DATASTORE_PATH
    file = '%d_%d_%d.h5' % (date.year, date.month, date.day)
    return os.path.join(rootdir, str(date.year), str(date.month), file)

def get_config_messages(cluster, station_id, date):
    """Get configuration messages

    :param cluster: string containing the cluster name
    :param station_id: station number
    :param date: date

    """
    path = get_data_path(date)

    file = tables.openFile(path)
    parent = file.getNode('/hisparc/cluster_%s/station_%d' %
                          (cluster.lower(), station_id))
    config = file.getNode(parent, 'config')
    blobs = file.getNode(parent, 'blobs')
    return file, config, blobs
