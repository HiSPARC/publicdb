import os
import re
import datetime
import tables

from django.conf import settings

def check_for_new_events(last_check_time):
    """Check for new events since last check

    Look for new events written to the datastore since the previous check.
    Actually, we don't really know what events are new.  For that, we need
    more metadata written by the data writer.  We can, however, look for
    file modification times and return the dates (filenames) of the new
    data.  By writing more metadata, we can improve this function.

    :param last_check_time: the timestamp of the previous check

    :return: a list of dates of the new events

    """

    rootdir = settings.DATASTORE_PATH
    date_list = []

    paths = os.listdir(rootdir)
    for path in paths:
        if re.match('[0-9]+', path):
            path = os.path.join(rootdir, path)
            for dirpath, dirnames, filenames in os.walk(path):
                for file in filenames:
                    mtime = os.path.getmtime(os.path.join(dirpath, file))
                    if mtime > last_check_time:
                        date = datetime.datetime.strptime(
                                    file, '%Y_%m_%d.h5').date()
                        if date != datetime.date.today():
                            date_list.append(date)

    return date_list

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
