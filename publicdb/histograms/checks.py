"""
Check for new data, and update summaries and flags.

"""
import datetime
import logging
import multiprocessing
import time

from . import datastore
from ..inforecords.models import Station
from .models import GeneratorState, NetworkSummary, Summary

logger = logging.getLogger(__name__)

# Tables supported by this code
SUPPORTED_TABLES = ['events', 'config', 'errors', 'weather', 'singles']
# Tables that initiate network updates
NETWORK_TABLES = {'events': 'coincidences'}
# Tables ignored by this code (unsupported tables not listed here will
# generate a warning).
IGNORE_TABLES = ['blobs']
# For some event tables, we can safely update the num_events during the
# check.  For events, for example, the histograms are recreated.  For
# configs, this is not possible.  The previous number of configs is used
# to select only new ones during the update.
RECORD_EARLY_NUM_EVENTS = ['events', 'weather', 'singles']


def check_for_updates():
    """Run a check for updates to the event tables"""

    state = GeneratorState.objects.get()

    if state.check_is_running:
        check_has_run = False
    else:
        check_for_new_events_and_update_flags(state)
        check_has_run = True

    return check_has_run


def check_for_new_events_and_update_flags(state):
    """Check the datastore for new events and update flags"""

    # bookkeeping
    last_check_time = time.mktime(state.check_last_run.timetuple())
    check_last_run = datetime.datetime.now()
    state.check_is_running = True
    state.save()

    try:
        # perform a check for updated files
        possibly_new = datastore.check_for_new_events(last_check_time)

        # perform a thorough check for each possible date
        for date, station_list in possibly_new.iteritems():
            process_possible_stations_for_date(date, station_list)
        state.check_last_run = check_last_run
    finally:
        # bookkeeping
        state.check_is_running = False
        state.save()


def process_possible_stations_for_date(date, station_list):
    """Check stations for possible new data

    :param date: The date which needs to be updated as a date object
    :param station_list: A nested dictionary:
                         {'[station_number]': {'[table_name]': [n_rows], }, }

    """
    logger.info('Now processing %s', date)
    unique_table_list = {table_name
                         for table_list in station_list.values()
                         for table_name in table_list.keys()}
    for table_name in unique_table_list:
        process_possible_tables_for_network(date, table_name)
    for station, table_list in station_list.iteritems():
        process_possible_tables_for_station(station, table_list, date)


def process_possible_tables_for_network(date, table_name):
    """Check table and store summary for the network

    :param date: The date which needs to be updated as a date object
    :param table_name: The name of the changed table (e.g. 'events')

    """
    try:
        update_flag_attr = 'needs_update_%s' % NETWORK_TABLES[table_name]
        logger.info("New %s data on %s.", table_name, date.strftime("%a %b %d %Y"))
        network_summary, _ = NetworkSummary.objects.get_or_create(date=date)
        setattr(network_summary, update_flag_attr, True)
        network_summary.needs_update = True
        network_summary.save()
    except KeyError:
        logger.debug('Unsupported table type for network: %s', table_name)


def process_possible_tables_for_station(station, table_list, date):
    """Check all tables and store summary for single station"""

    try:
        station = Station.objects.get(number=station)
    except Station.DoesNotExist:
        logger.error('Unknown station: %s', station)
    else:
        summary, created = Summary.objects.get_or_create(station=station, date=date)
        for table, num_events in table_list.iteritems():
            check_table_and_update_flags(table, num_events, summary)


def check_table_and_update_flags(table_name, num_events, summary):
    """Check a single table and update flags if new data"""

    if table_name in SUPPORTED_TABLES:
        number_of_events_attr = 'num_%s' % table_name
        update_flag_attr = 'needs_update_%s' % table_name

        if getattr(summary, number_of_events_attr) != num_events:
            logger.info("New data (%s) on %s for station %d",
                        table_name,
                        summary.date.strftime("%a %b %d %Y"),
                        summary.station.number)
            # only record number of events for *some* tables at this time
            if table_name in RECORD_EARLY_NUM_EVENTS:
                setattr(summary, number_of_events_attr, num_events)
            setattr(summary, update_flag_attr, True)
            summary.needs_update = True
            summary.save()
    elif table_name not in IGNORE_TABLES:
        logger.warning('Unsupported table type: %s', table_name)
