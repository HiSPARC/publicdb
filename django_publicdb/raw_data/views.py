from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, StreamingHttpResponse)
from django.shortcuts import get_object_or_404, render
from django.template import loader, Context
from django.conf import settings
from django.db.models import Q

import os
import tables
import datetime
import urlparse
import tempfile
import csv
import calendar
import urllib

import dateutil.parser

from sapphire.analysis.coincidence_queries import CoincidenceQuery

from django_publicdb.inforecords.models import Station, Cluster
from django_publicdb.histograms.models import Summary, NetworkSummary
from django_publicdb.histograms import esd
from django_publicdb.raw_data.forms import (DataDownloadForm,
                                            CoincidenceDownloadForm)

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
dispatcher = SimpleXMLRPCDispatcher()


class SingleLineStringIO:
    """Very limited file-like object buffering a single line."""

    def write(self, line):
        self.line = line


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
def get_data_url(station_number, date, get_blobs=False):
    """Return a link to a file containing requested data

    Based on the given parameters, copy requested data to a temporary file
    and provide a link to download that file.

    :param station_number: the HiSPARC station number
    :param date: a xmlrpclib.DateTime instance; retrieve events from this
        day

    """
    date = date.timetuple()

    datafile = get_raw_datafile(date)
    station_node = get_station_node(datafile, station_number)
    target = get_target()

    if get_blobs:
        datafile.copy_node(station_node, target.root, recursive=True)
    else:
        datafile.copy_node(station_node, target.root, recursive=False)
        target_node = target.get_node('/', station_node._v_name)
        for node in station_node:
            if node.name != 'blobs':
                datafile.copy_node(node, target_node)

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
        datafile = tables.open_file(name, 'r')
    except IOError:
        raise Exception("No data for that date")

    return datafile


def get_station_node(datafile, station_number):
    """Return the requested station's node"""

    station = 'station_%d' % station_number

    for cluster in datafile.list_nodes('/hisparc'):
        if station in cluster:
            return datafile.get_node(cluster, station)

    raise Exception("No data available for this station on that date")


def get_target():
    """Return a reference to a download target file"""

    dir = os.path.join(settings.MEDIA_ROOT, 'raw_data')
    with tempfile.NamedTemporaryFile(suffix='.h5', dir=dir,
                                     delete=False) as file:
        pass
    #FIXME (for debugging only, sets extra permissions)
    #os.chmod(file.name, 0644)
    return tables.open_file(file.name, 'w')


def download_form(request, station_number=None, start=None, end=None):
    if request.method == 'POST':
        form = DataDownloadForm(request.POST)
        if form.is_valid():
            station = form.cleaned_data['station']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            download = form.cleaned_data['download']
            data_type = form.cleaned_data['data_type']
            query_string = urllib.urlencode({'start': start, 'end': end,
                                             'download': download})
            return HttpResponseRedirect('/data/%d/%s/?%s' %
                                        (station.number, data_type,
                                         query_string))
    else:
        if station_number:
            station = get_object_or_404(Station, number=station_number)
        else:
            station = None
        form = DataDownloadForm(initial={'station': station,
                                         'start': start,
                                         'end': end,
                                         'data_type': 'events'})

    return render(request, 'data_download.html', {'form': form})


def download_data(request, station_number, data_type='events'):
    """Download data.

    :param station_number: station number
    :param data_type: (optional) choose between event and weather data
    :param start: (optional, GET) start of data range
    :param end: (optional, GET) end of data range
    :param download: (optional, GET) download the csv

    """
    station_number = int(station_number)
    station = get_object_or_404(Station, number=station_number)

    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = datetime.datetime.combine(yesterday, datetime.time())

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

    download = request.GET.get('download', False)
    if download in ['true', 'True']:
        download = True
    else:
        download = False

    timerange_string = prettyprint_timerange(start, end)
    if data_type == 'weather':
        csv_output = generate_weather_as_csv(station, start, end)
        filename = 'weather-s%d-%s.csv' % (station_number, timerange_string)
    elif data_type == 'events':
        csv_output = generate_events_as_csv(station, start, end)
        filename = 'events-s%d-%s.csv' % (station_number, timerange_string)

    response = StreamingHttpResponse(csv_output, content_type='text/csv')

    if download:
        content_disposition = 'attachment; filename="%s"' % filename
    else:
        content_disposition = 'inline; filename="%s"' % filename
    response['Content-Disposition'] = content_disposition
    response['Access-Control-Allow-Origin'] = '*'

    return response


def generate_events_as_csv(station, start, end):
    """Render CSV output as an iterator."""

    t = loader.get_template('event_data.csv')
    c = Context({'station': station, 'start': start, 'end': end})

    yield t.render(c)

    line_buffer = SingleLineStringIO()
    writer = csv.writer(line_buffer, delimiter='\t')
    events_returned = False

    events = get_events_from_esd_in_range(station, start, end)
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
               clean_floats(event['t_trigger'])]
        writer.writerow(row)
        yield line_buffer.line
        events_returned = True

    if not events_returned:
        yield "# No events found for the chosen query."


def get_events_from_esd_in_range(station, start, end):
    """Get events from ESD in time range.

    :param station: Station object
    :param start: start of datetime range
    :param end: end of datetime range

    """
    for t0, t1 in single_day_ranges(start, end):
        try:
            Summary.objects.get(station=station, date=t0)
        except Summary.DoesNotExist:
            continue
        filepath = esd.get_esd_data_path(t0)
        try:
            with tables.open_file(filepath) as f:
                station_node = esd.get_station_node(f, station)
                ts0 = calendar.timegm(t0.utctimetuple())
                ts1 = calendar.timegm(t1.utctimetuple())
                for event in station_node.events.where(
                        '(ts0 <= timestamp) & (timestamp < ts1)'):
                    yield event
        except (IOError, tables.NoSuchNodeError):
            continue


def generate_weather_as_csv(station, start, end):
    """Render CSV output as an iterator."""

    t = loader.get_template('weather_data.csv')
    c = Context({'station': station, 'start': start, 'end': end})

    yield t.render(c)

    line_buffer = SingleLineStringIO()
    writer = csv.writer(line_buffer, delimiter='\t')
    weather_returned = False

    events = get_weather_from_esd_in_range(station, start, end)
    for event in events:
        dt = datetime.datetime.utcfromtimestamp(event['timestamp'])
        row = [dt.date(), dt.time(),
               event['timestamp'],
               clean_floats(event['temp_inside'], precision=2),
               clean_floats(event['temp_outside'], precision=2),
               event['humidity_inside'],
               event['humidity_outside'],
               clean_floats(event['barometer'], precision=2),
               event['wind_dir'],
               event['wind_speed'],
               event['solar_rad'],
               event['uv'],
               clean_floats(event['evapotranspiration'], precision=3),
               clean_floats(event['rain_rate'], precision=2),
               event['heat_index'],
               clean_floats(event['dew_point'], precision=2),
               clean_floats(event['wind_chill'], precision=2),
              ]
        writer.writerow(row)
        yield line_buffer.line
        weather_returned = True

    if not weather_returned:
        yield "# No weather data found for the chosen query."


def get_weather_from_esd_in_range(station, start, end):
    """Get weather from ESD in time range.

    :param station: Station object
    :param start: start of datetime range
    :param end: end of datetime range

    """
    for t0, t1 in single_day_ranges(start, end):
        try:
            Summary.objects.get(station=station, date=t0,
                                num_weather__isnull=False)
        except Summary.DoesNotExist:
            continue
        filepath = esd.get_esd_data_path(t0)
        try:
            with tables.open_file(filepath) as f:
                station_node = esd.get_station_node(f, station)
                ts0 = calendar.timegm(t0.utctimetuple())
                ts1 = calendar.timegm(t1.utctimetuple())
                for event in station_node.weather.where(
                        '(ts0 <= timestamp) & (timestamp < ts1)'):
                    yield event
        except (IOError, tables.NoSuchNodeError):
            continue


def coincidences_download_form(request, start=None, end=None):
    if request.method == 'POST':
        form = CoincidenceDownloadForm(request.POST)
        if form.is_valid():
            cluster = form.cleaned_data['cluster']
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            n = form.cleaned_data['n']
            download = form.cleaned_data['download']
            query_string = urllib.urlencode({'cluster': cluster,
                                             'start': start, 'end': end,
                                             'n': n, 'download': download})
            return HttpResponseRedirect('/data/network/coincidences/?%s' %
                                        query_string)
    else:
        form = CoincidenceDownloadForm(initial={'start': start,'end': end,
                                                'n': 2})

    return render(request, 'coincidences_download.html', {'form': form})


def download_coincidences(request):
    """Download coincidences.

    :param stations: (optional, GET) station numbers, only coincidences with
                     stations specified are returned
    :param cluster: (optional, GET) cluster name, only coincidences with
                    stations in the specified cluster are returned
    :param start: (optional, GET) start of data range
    :param end: (optional, GET) end of data range
    :param n: (optional, GET) minimum number of events in a coincidence
    :param download: (optional, GET) download the csv

    """
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    yesterday = datetime.datetime.combine(yesterday, datetime.time())

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

    stations = request.GET.get('stations', None)
    if stations == 'None':
        stations = None

    cluster = request.GET.get('cluster', None)
    if cluster == 'None':
        cluster = None

    if stations and cluster:
        msg = "Both stations and cluster are defined."
        return HttpResponseBadRequest(msg, content_type="text/plain")
    elif stations:
        stations = [int(number) for number in stations.strip('[]').split(',')]
        if len(stations) >= 30:
            msg = "To many stations in query, use less than 30."
            return HttpResponseBadRequest(msg, content_type="text/plain")
        if Station.objects.filter(number__in=stations).count() != len(stations):
            msg = "Not all stations are valid."
            return HttpResponseBadRequest(msg, content_type="text/plain")
    elif cluster:
        cluster = get_object_or_404(Cluster, name=cluster)
        stations = (Station.objects.filter(Q(cluster__parent=cluster) |
                                           Q(cluster=cluster))
                                   .values_list('number', flat=True))

    n = int(request.GET.get('n', '2'))

    download = request.GET.get('download', False)
    if download in ['true', 'True']:
        download = True
    else:
        download = False

    timerange_string = prettyprint_timerange(start, end)
    csv_output = generate_coincidences_as_csv(start, end, cluster, stations, n)
    filename = 'coincidences-%s.csv' % (timerange_string)

    response = StreamingHttpResponse(csv_output, content_type='text/csv')

    if download:
        content_disposition = 'attachment; filename="%s"' % filename
    else:
        content_disposition = 'inline; filename="%s"' % filename
    response['Content-Disposition'] = content_disposition
    response['Access-Control-Allow-Origin'] = '*'

    return response


def generate_coincidences_as_csv(start, end, cluster, stations, n):
    """Render CSV output as an iterator."""

    t = loader.get_template('coincidences.csv')
    c = Context({'start': start, 'end': end, 'cluster': cluster,
                 'stations': stations, 'n': n})

    yield t.render(c)

    line_buffer = SingleLineStringIO()
    writer = csv.writer(line_buffer, delimiter='\t')
    coincidences_returned = False

    for id, number, event in get_coincidences_from_esd_in_range(start, end,
                                                                stations, n):
        dt = datetime.datetime.utcfromtimestamp(event['timestamp'])
        row = [id,
               number,
               dt.date(), dt.time(),
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
               clean_floats(event['t_trigger'])]
        writer.writerow(row)
        yield line_buffer.line
        coincidences_returned = True

    if not coincidences_returned:
        yield "# No coincidences found for the chosen query."

def get_coincidences_from_esd_in_range(start, end, stations, n):
    """Get coincidences from ESD in time range.

    :param start: start of datetime range
    :param end: end of datetime range
    :param stations: station numbers
    :param n: minimum number of events in coincidence
    :yield: id, station number and event

    """
    id = -1
    for t0, t1 in single_day_ranges(start, end):
        try:
            NetworkSummary.objects.get(date=t0)
        except NetworkSummary.DoesNotExist:
            continue
        with tables.open_file(esd.get_esd_data_path(t0)) as f:
            try:
                cq = CoincidenceQuery(f)
                ts0 = calendar.timegm(t0.utctimetuple())
                ts1 = calendar.timegm(t1.utctimetuple())
                if stations:
                    coincidences = cq.at_least(stations, n, start=ts0, stop=ts1)
                    events = cq.events_from_stations(coincidences, stations, n)
                else:
                    coincidences = cq.timerange(start=ts0, stop=ts1)
                    events = cq.all_events(coincidences, n)
                for id, coin in enumerate(events, id + 1):
                    for number, event in coin:
                        yield id, number, event
            except (IOError, tables.NoSuchNodeError):
                continue


def get_coincidence_events(f, coincidence):
    """Get events for a coincidence from an ESD file

    :param f: PyTables file handle for an ESD file
    :param coincidence: A coincidence row

    """
    coincidences_node = esd.get_coincidences_node(f)
    c_idx = coincidences_node.c_index[coincidence['id']]
    for s_idx, e_idx in c_idx:
        s_path = coincidences_node.s_index[s_idx]
        number = int(s_path.split('station_')[-1])
        s_group = f.get_node(s_path)
        event = s_group.events[e_idx]
        yield number, event


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


def single_day_ranges(start, end):
    """Generate datetime ranges consisting of a single day.

    Generate datetime ranges, a single day at a time.  The generator keeps
    returning two datetime values, making up a range of a full day.
    However, the first and last days may be shorter, if a specific
    time-of-day was specified.

    :param start: start of range
    :param end: end of range

    """
    cur = start
    next_day = (cur.replace(hour=0, minute=0, second=0, microsecond=0) +
                datetime.timedelta(days=1))

    while next_day < end:
        yield cur, next_day
        cur = next_day
        next_day = cur + datetime.timedelta(days=1)
    yield cur, end
