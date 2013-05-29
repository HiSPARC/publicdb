from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.template import loader, Context
from django.conf import settings

import os
import tables
import datetime
import urlparse
import tempfile
import csv
import calendar

import dateutil.parser

from django_publicdb.inforecords.models import Station
from django_publicdb.histograms.models import Summary
from django_publicdb.histograms import esd


from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
dispatcher = SimpleXMLRPCDispatcher()


def call_xmlrpc(request):
    """Dispatch XML-RPC requests."""
    if request.method == 'POST':
        # Process XML-RPC call
        response = HttpResponse(mimetype='text/xml')
        response.write(dispatcher._marshaled_dispatch(request.body))
        response['Content-length'] = str(len(response.content))
        return response
    else:
        # Show documentation on available methods
        response = HttpResponse()
        t = loader.get_template('rawdata/xmlrpc.html')
        methods = []
        for method in dispatcher.system_listMethods():
            methods.append({'name': method,
                            'help': dispatcher.system_methodHelp(method)})
        c = Context({'methods': methods})
        response.write(t.render(c))
        return response


def xmlrpc(uri):
    """A decorator for XML-RPC functions."""
    def register_xmlrpc(fn):
        dispatcher.register_function(fn, uri)
        return fn
    return register_xmlrpc


@xmlrpc('hisparc.get_data_url')
def get_data_url(station_id, date, get_blobs=False):
    """Return a link to a file containing requested data

    Based on the given parameters, copy requested data to a temporary file
    and provide a link to download that file.

    :param station_id: the HiSPARC station number
    :param date: a xmlrpclib.DateTime instance; retrieve events from this
        day

    """
    date = date.timetuple()

    datafile = get_raw_datafile(date)
    station_node = get_station_node(datafile, station_id)
    target = get_target()

    if get_blobs:
        datafile.copyNode(station_node, target.root, recursive=True)
    else:
        datafile.copyNode(station_node, target.root, recursive=False)
        target_node = target.getNode('/', station_node._v_name)
        for node in station_node:
            if node.name != 'blobs':
                datafile.copyNode(node, target_node)

    url = urlparse.urljoin(settings.MEDIA_URL, 'raw_data/')
    url = urlparse.urljoin(url, os.path.basename(target.filename))

    datafile.close()
    target.close()

    return url


def get_raw_datafile(date):
    """Return a reference to the raw data file on a specified date"""

    dir = os.path.join(settings.DATASTORE_PATH, '%d/%d' % (date.tm_year,
                                                           date.tm_mon))
    name = os.path.join(dir, '%d_%d_%d.h5' % (date.tm_year, date.tm_mon,
                                              date.tm_mday))
    try:
        datafile = tables.openFile(name, 'r')
    except IOError:
        raise Exception("No data for that date")

    return datafile


def get_station_node(datafile, station_id):
    """Return the requested station's node"""

    station = 'station_%d' % station_id

    for cluster in datafile.listNodes('/hisparc'):
        if station in cluster:
            return datafile.getNode(cluster, station)

    raise Exception("No data available for this station on that date")


def get_target():
    """Return a reference to a download target file"""

    dir = os.path.join(settings.MEDIA_ROOT, 'raw_data')
    with tempfile.NamedTemporaryFile(suffix='.h5', dir=dir,
                                     delete=False) as file:
        pass
    #FIXME (for debugging only, sets extra permissions)
    #os.chmod(file.name, 0644)
    return tables.openFile(file.name, 'w')


def download_events(request, station_id):
    """Download events.

    :param station_id: station id
    :param start: (optional, GET) start of data range
    :param end: (optional, GET) end of data range

    """
    station_id = int(station_id)
    station = get_object_or_404(Station, number=station_id)

    yesterday = datetime.date.today() - datetime.timedelta(days=1)

    try:
        if 'start' in request.GET:
            start = dateutil.parser.parse(request.GET['start'])
        else:
            start = yesterday

        if 'end' in request.GET:
            end = dateutil.parser.parse(request.GET['end'])
        else:
            end = start + datetime.timedelta(days=1)
    except ValueError:
        msg = ("Incorrect optional parameters (start [datetime], "
               "end [datetime])")
        return HttpResponseBadRequest(msg, content_type="text/plain")

    events = get_events_from_esd_in_range(station, start, end)

    t = loader.get_template('event_data.csv')
    c = Context({'station': station, 'start': start, 'end': end})
    
    response = HttpResponse(content_type='text/csv')
    timerange_string = prettyprint_timerange(start, end)
    filename = 'events-s%d-%s.csv' % (station_id, timerange_string)
    response['Content-Disposition'] = 'filename="%s"' % filename
    response.write(t.render(c))

    writer = csv.writer(response, delimiter='\t')
    for event in events:
        dt = datetime.datetime.utcfromtimestamp(event['timestamp'])
        row = [dt.date(), dt.time(),
               event['timestamp'],
               event['nanoseconds'],
               event['pulseheights'][0],
               event['pulseheights'][1],
               event['pulseheights'][2],
               event['pulseheights'][3],
               event['integrals'][0],
               event['integrals'][1],
               event['integrals'][2],
               event['integrals'][3],
               clean_floats(event['n1']),
               clean_floats(event['n2']),
               clean_floats(event['n3']),
               clean_floats(event['n4']),
               clean_floats(event['t1']),
               clean_floats(event['t2']),
               clean_floats(event['t3']),
               clean_floats(event['t4']),
              ]
        writer.writerow(row)

    return response


def get_events_from_esd_in_range(station, start, end):
    """Get events from ESD in time range.

    :param station: Station object
    :param start: start of datetime range
    :param end: end of datetime range

    """
    get_object_or_404(Summary, station=station, date=start)
    filepath = esd.get_esd_data_path(start)
    with tables.openFile(filepath) as f:
        station_node = esd.get_station_node(f, station)
        ts0 = calendar.timegm(start.utctimetuple())
        ts1 = calendar.timegm(end.utctimetuple())
        for event in station_node.events.where(
            '(ts0 <= timestamp) & (timestamp < ts1)'):
            yield event


def clean_floats(number, precision=4):
    """Format floating point numbers for data download."""

    if int(number) in [-1, -999]:
        return int(number)
    else:
        return round(number, precision)


def prettyprint_timerange(t0, t1):
    """Pretty print a time range."""

    duration = t1 - t0
    if (duration.seconds > 0 or t0.second > 0 or t0.minute > 0 or
        t0.hour > 0):
        timerange = '%s %s' % (t0, t1)
    elif duration.days == 1:
        timerange = str(t0.date())
    else:
        timerange = '%s %s' % (t0.date(), t1.date())

    timerange = (timerange.replace('-', '').replace(' ', '_')
                          .replace(':', ''))
    return timerange
