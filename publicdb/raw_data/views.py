import calendar
import csv
import datetime
import os
import tempfile
import urllib
import urlparse

from cStringIO import StringIO
from SimpleXMLRPCServer import SimpleXMLRPCDispatcher

import dateutil.parser
import tables

from numpy import char, column_stack, degrees, empty, isnan, where

from django.conf import settings
from django.db.models import Q
from django.http import (HttpResponse, HttpResponseBadRequest,
                         HttpResponseRedirect, StreamingHttpResponse)
from django.shortcuts import get_object_or_404, render
from django.template import Context, loader

from sapphire import CoincidenceQuery

from . import knmi_lightning
from ..histograms import esd
from ..histograms.models import NetworkSummary, Summary
from ..inforecords.models import Cluster, Station
from .date_generator import single_day_ranges
from .forms import CoincidenceDownloadForm, DataDownloadForm

dispatcher = SimpleXMLRPCDispatcher()


MIME_PLAIN = 'text/plain'
MIME_TSV = 'text/tab-separated-values'
MIME_XML = 'text/xml'


class SingleLineStringIO:
    """Very limited file-like object buffering a single line."""

    def write(self, line):
        self.line = line


def call_xmlrpc(request):
    """Dispatch XML-RPC requests."""

    if request.method == 'POST':
        # Process XML-RPC call
        response = HttpResponse(content_type=MIME_XML)
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
    # FIXME (for debugging only, sets extra permissions)
    # os.chmod(file.name, 0644)
    return tables.open_file(file.name, 'w')


def download_form(request, station_number=None, start=None, end=None):
    if request.GET:
        form = DataDownloadForm(request.GET)
        if form.is_valid():
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            download = form.cleaned_data['download']
            data_type = form.cleaned_data['data_type']
            query_string = urllib.urlencode({'start': start, 'end': end,
                                             'download': download})
            if data_type == 'lightning':
                lightning_type = form.cleaned_data['lightning_type']
                return HttpResponseRedirect('/data/knmi/%s/%s/?%s' %
                                            (data_type, lightning_type,
                                             query_string))
            else:
                station = form.cleaned_data['station']
                return HttpResponseRedirect('/data/%d/%s/?%s' %
                                            (station.number, data_type,
                                             query_string))
    else:
        if station_number:
            station = get_object_or_404(Station, number=station_number)
        else:
            station = None
        form = DataDownloadForm(initial={'station_events': station,
                                         'station_weather': station,
                                         'station_singles': station,
                                         'start': start,
                                         'end': end,
                                         'data_type': 'events'})

    return render(request, 'data_download.html', {'form': form})


def download_data(request, data_type='events', station_number=None,
                  lightning_type=None):
    """Download data.

    :param data_type: (optional) choose between event, weather, and
                      lightning data
    :param station_number: (optional) station number, required for event
                           and weather data
    :param lightning_type: (optional) lightning type, required for lightning
                           data
    :param start: (optional, GET) start of data range
    :param end: (optional, GET) end of data range
    :param download: (optional, GET) download the tsv

    """
    if data_type in ['events', 'weather', 'singles']:
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
        return HttpResponseBadRequest(msg, content_type=MIME_PLAIN)

    download = request.GET.get('download', False)
    if download in ['true', 'True']:
        download = True
    else:
        download = False

    timerange_string = prettyprint_timerange(start, end)
    if data_type == 'events':
        tsv_output = generate_events_as_tsv(station, start, end)
        filename = 'events-s%d-%s.tsv' % (station_number, timerange_string)
    elif data_type == 'weather':
        tsv_output = generate_weather_as_tsv(station, start, end)
        filename = 'weather-s%d-%s.tsv' % (station_number, timerange_string)
    elif data_type == 'singles':
        tsv_output = generate_singles_as_tsv(station, start, end)
        filename = 'singles-s%d-%s.tsv' % (station_number, timerange_string)
    elif data_type == 'lightning':
        lightning_type = int(lightning_type)
        if lightning_type not in range(6):
            msg = ("Incorrect lightning type, should be a value between 0-5")
            return HttpResponseBadRequest(msg, content_type=MIME_PLAIN)
        tsv_output = generate_lightning_as_tsv(lightning_type, start, end)
        filename = 'lightning-knmi-%s.tsv' % (timerange_string)

    response = StreamingHttpResponse(tsv_output, content_type=MIME_TSV)

    if download:
        content_disposition = 'attachment; filename="%s"' % filename
    else:
        content_disposition = 'inline; filename="%s"' % filename
    response['Content-Disposition'] = content_disposition
    response['Access-Control-Allow-Origin'] = '*'

    return response


def generate_events_as_tsv(station, start, end):
    """Render TSV output as an iterator."""

    t = loader.get_template('event_data.tsv')
    c = Context({'station': station, 'start': start, 'end': end})

    yield t.render(c)

    events_returned = False

    events_reconstructions = get_events_from_esd_in_range(station, start, end)
    for events, reconstructions in events_reconstructions:
        if not len(events):
            continue
        dt = events['timestamp'].astype('datetime64[s]')
        data = column_stack([
            dt.astype('datetime64[D]'),
            [value.time() for value in dt.tolist()],
            events['timestamp'],
            events['nanoseconds'],
            events['pulseheights'][:, 0],
            events['pulseheights'][:, 1],
            events['pulseheights'][:, 2],
            events['pulseheights'][:, 3],
            events['integrals'][:, 0],
            events['integrals'][:, 1],
            events['integrals'][:, 2],
            events['integrals'][:, 3],
            clean_float_array(events['n1']),
            clean_float_array(events['n2']),
            clean_float_array(events['n3']),
            clean_float_array(events['n4']),
            clean_float_array(events['t1']),
            clean_float_array(events['t2']),
            clean_float_array(events['t3']),
            clean_float_array(events['t4']),
            clean_float_array(events['t_trigger']),
            clean_angle_array(reconstructions['zenith']),
            clean_angle_array(reconstructions['azimuth'])])
        block_buffer = StringIO()
        writer = csv.writer(block_buffer, delimiter='\t', lineterminator='\n')
        writer.writerows(data)
        yield block_buffer.getvalue()
        events_returned = True

    if not events_returned:
        yield "# No events found for the chosen query."
    else:
        yield "# Finished downloading."


def get_events_from_esd_in_range(station, start, end):
    """Get events from ESD in time range.

    :param station: Station object
    :param start: start of datetime range
    :param end: end of datetime range

    """
    for t0, t1 in single_day_ranges(start, end):
        try:
            Summary.objects.get(station=station, date=t0,
                                num_events__isnull=False)
        except Summary.DoesNotExist:
            continue
        filepath = esd.get_esd_data_path(t0)
        try:
            with tables.open_file(filepath) as f:
                try:
                    station_node = esd.get_station_node(f, station)
                    events_table = station_node.events
                except tables.NoSuchNodeError:
                    continue
                try:
                    reconstructions_table = station_node.reconstructions
                except tables.NoSuchNodeError:
                    reconstructions_table = FakeReconstructionsTable()
                if (t1 - t0).days == 1:
                    events = events_table.read()
                    reconstructions = reconstructions_table[events['event_id']]
                else:
                    ts0 = calendar.timegm(t0.utctimetuple())  # noqa: F841
                    ts1 = calendar.timegm(t1.utctimetuple())  # noqa: F841
                    event_ids = events_table.get_where_list(
                        '(ts0 <= timestamp) & (timestamp < ts1)')
                    events = events_table.read_coordinates(event_ids)
                    reconstructions = reconstructions_table[event_ids]
        except IOError:
            continue
        else:
            yield events, reconstructions


def generate_weather_as_tsv(station, start, end):
    """Render TSV output as an iterator."""

    t = loader.get_template('weather_data.tsv')
    c = Context({'station': station, 'start': start, 'end': end})

    yield t.render(c)

    weather_returned = False

    weather_events = get_weather_from_esd_in_range(station, start, end)
    for events in weather_events:
        dt = events['timestamp'].astype('datetime64[s]')
        data = column_stack([
            dt.astype('datetime64[D]'),
            [value.time() for value in dt.tolist()],
            events['timestamp'],
            clean_float_array(events['temp_inside']),
            clean_float_array(events['temp_outside']),
            events['humidity_inside'],
            events['humidity_outside'],
            clean_float_array(events['barometer']),
            events['wind_dir'],
            events['wind_speed'],
            events['solar_rad'],
            events['uv'],
            clean_float_array(events['evapotranspiration']),
            clean_float_array(events['rain_rate']),
            events['heat_index'],
            clean_float_array(events['dew_point']),
            clean_float_array(events['wind_chill'])])
        block_buffer = StringIO()
        writer = csv.writer(block_buffer, delimiter='\t', lineterminator='\n')
        writer.writerows(data)
        yield block_buffer.getvalue()
        weather_returned = True

    if not weather_returned:
        yield "# No weather data found for the chosen query."
    else:
        yield "# Finished downloading."


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
                if (t1 - t0).days == 1:
                    events = station_node.weather.read()
                else:
                    ts0 = calendar.timegm(t0.utctimetuple())  # noqa: F841
                    ts1 = calendar.timegm(t1.utctimetuple())  # noqa: F841
                    events = station_node.weather.read_where(
                        '(ts0 <= timestamp) & (timestamp < ts1)')
        except (IOError, tables.NoSuchNodeError):
            continue
        else:
            yield events


def generate_singles_as_tsv(station, start, end):
    """Render TSV output as an iterator."""

    t = loader.get_template('singles_data.tsv')
    c = Context({'station': station, 'start': start, 'end': end})

    yield t.render(c)

    singles_returned = False

    singles_events = get_singles_from_esd_in_range(station, start, end)
    for events in singles_events:
        dt = events['timestamp'].astype('datetime64[s]')
        data = column_stack([
            dt.astype('datetime64[D]'),
            [value.time() for value in dt.tolist()],
            events['timestamp'],
            events['mas_ch1_low'],
            events['mas_ch1_high'],
            events['mas_ch2_low'],
            events['mas_ch2_high'],
            events['slv_ch1_low'],
            events['slv_ch1_high'],
            events['slv_ch2_low'],
            events['slv_ch2_high']])
        block_buffer = StringIO()
        writer = csv.writer(block_buffer, delimiter='\t', lineterminator='\n')
        writer.writerows(data)
        yield block_buffer.getvalue()
        singles_returned = True

    if not singles_returned:
        yield "# No singles data found for the chosen query."
    else:
        yield "# Finished downloading."


def get_singles_from_esd_in_range(station, start, end):
    """Get singles from ESD in time range.

    :param station: Station object
    :param start: start of datetime range
    :param end: end of datetime range

    """
    for t0, t1 in single_day_ranges(start, end):
        try:
            Summary.objects.get(station=station, date=t0,
                                num_singles__isnull=False)
        except Summary.DoesNotExist:
            continue
        filepath = esd.get_esd_data_path(t0)
        try:
            with tables.open_file(filepath) as f:
                station_node = esd.get_station_node(f, station)
                if (t1 - t0).days == 1:
                    events = station_node.singles.read()
                else:
                    ts0 = calendar.timegm(t0.utctimetuple())  # noqa: F841
                    ts1 = calendar.timegm(t1.utctimetuple())  # noqa: F841
                    events = station_node.singles.read_where(
                        '(ts0 <= timestamp) & (timestamp < ts1)')
        except (IOError, tables.NoSuchNodeError):
            continue
        else:
            yield events


def generate_lightning_as_tsv(lightning_type, start, end):
    """Render TSV output as an iterator."""

    types = ('Single-point', 'Cloud-cloud', 'Cloud-cloud mid',
             'Cloud-cloud end', 'Cloud-ground', 'Cloud-ground return')
    type_str = '%d: %s' % (lightning_type, types[lightning_type])

    t = loader.get_template('lightning_data.tsv')
    c = Context({'lightning_type': type_str, 'start': start, 'end': end})

    yield t.render(c)

    line_buffer = SingleLineStringIO()
    writer = csv.writer(line_buffer, delimiter='\t', lineterminator='\n')
    lightning_returned = False

    events = get_lightning_in_range(lightning_type, start, end)
    for event in events:
        dt = datetime.datetime.utcfromtimestamp(event['timestamp'])
        row = [dt.date(), dt.time(),
               event['timestamp'],
               event['nanoseconds'],
               clean_floats(event['latitude'], precision=6),
               clean_floats(event['longitude'], precision=6),
               int(event['current'])]
        writer.writerow(row)
        yield line_buffer.line
        lightning_returned = True

    if not lightning_returned:
        yield "# No lightning data found for the chosen query."
    else:
        yield "# Finished downloading."


def get_lightning_in_range(lightning_type, start, end):
    """Get lightning in time range.

    :param lightning_type: lighting of specific type
    :param start: start of datetime range
    :param end: end of datetime range

    """
    for t0, t1 in single_day_ranges(start, end):
        filepath = knmi_lightning.data_path(t0)
        try:
            with tables.open_file(filepath) as f:
                ts0 = calendar.timegm(t0.utctimetuple())
                ts1 = calendar.timegm(t1.utctimetuple())
                for event in knmi_lightning.discharges(f, ts0, ts1,
                                                       type=lightning_type):
                    yield event
        except (IOError, tables.NoSuchNodeError):
            continue


def coincidences_download_form(request, start=None, end=None):
    if request.GET:
        form = CoincidenceDownloadForm(request.GET)
        if form.is_valid():
            cluster = form.cleaned_data.get('cluster')
            stations = form.cleaned_data.get('stations')
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            n = form.cleaned_data['n']
            download = form.cleaned_data['download']
            query_string = urllib.urlencode({'cluster': cluster,
                                             'stations': stations,
                                             'start': start, 'end': end,
                                             'n': n, 'download': download})
            return HttpResponseRedirect('/data/network/coincidences/?%s' %
                                        query_string)
    else:
        form = CoincidenceDownloadForm(initial={'filter_by': 'network',
                                                'start': start, 'end': end,
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
    :param download: (optional, GET) download the tsv

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
        error_msg = ("Incorrect optional parameters (start [datetime], "
                     "end [datetime])")
        return HttpResponseBadRequest(error_msg, content_type=MIME_PLAIN)

    n = int(request.GET.get('n', '2'))

    stations = request.GET.get('stations', None)
    if stations == 'None':
        stations = None

    cluster = request.GET.get('cluster', None)
    if cluster == 'None':
        cluster = None

    error_msg = None
    if stations and cluster:
        error_msg = "Both stations and cluster are defined."
    elif stations:
        try:
            stations = [int(number.strip('"\' '))
                        for number in stations.strip('[](), ').split(',')]
        except ValueError:
            error_msg = "Unable to parse station numbers."
        if len(stations) < n:
            error_msg = "To few stations in query, give at least n."
        if len(stations) >= 30:
            error_msg = "To many stations in query, use less than 30."
        if (Station.objects.filter(number__in=stations).count() !=
                len(stations)):
            error_msg = "Not all station numbers are valid."
    elif cluster:
        cluster = get_object_or_404(Cluster, name=cluster)
        stations = (Station.objects.filter(Q(cluster__parent=cluster) |
                                           Q(cluster=cluster))
                                   .values_list('number', flat=True))
        if len(stations) >= 30:
            error_msg = ("To many stations in this cluster, "
                         "manually select a subset of stations.")

    if error_msg is not None:
        return HttpResponseBadRequest(error_msg, content_type=MIME_PLAIN)

    download = request.GET.get('download', False)
    if download in ['true', 'True']:
        download = True
    else:
        download = False

    timerange_string = prettyprint_timerange(start, end)
    tsv_output = generate_coincidences_as_tsv(start, end, cluster, stations, n)
    filename = 'coincidences-%s.tsv' % (timerange_string)

    response = StreamingHttpResponse(tsv_output, content_type=MIME_TSV)

    if download:
        content_disposition = 'attachment; filename="%s"' % filename
    else:
        content_disposition = 'inline; filename="%s"' % filename
    response['Content-Disposition'] = content_disposition
    response['Access-Control-Allow-Origin'] = '*'

    return response


def generate_coincidences_as_tsv(start, end, cluster, stations, n):
    """Render TSV output as an iterator."""

    t = loader.get_template('coincidences.tsv')
    c = Context({'start': start, 'end': end, 'cluster': cluster,
                 'stations': stations, 'n': n})

    yield t.render(c)

    line_buffer = SingleLineStringIO()
    writer = csv.writer(line_buffer, delimiter='\t', lineterminator='\n')
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
               clean_floats(event['t_trigger']),
               -999, -999]
        writer.writerow(row)
        yield line_buffer.line
        coincidences_returned = True

    if not coincidences_returned:
        yield "# No coincidences found for the chosen query."
    else:
        yield "# Finished downloading."


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
                    coincidences = cq.at_least(stations, n, start=ts0,
                                               stop=ts1)
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


def clean_float_array(numbers, precision=5):
    """Format floating point numbers for data download.

    :param numbers: array like list of values
    :param precision: the number of significant numbers, this includes
                      numbers to the left of the decimal. Must be 3 or higher,
                      to support -999.

    """
    if precision < 3:
        # Unable to preserve -999 if precision less than 3.
        precision = 3
    return char.mod('%%.%dg' % precision, numbers)


def clean_floats(number, precision=4):
    """Format floating point numbers for data download."""

    if int(number) in [-1, -999]:
        return int(number)
    else:
        return round(number, precision)


def clean_angle_array(angles):
    """Convert radians to degrees, but only if not -999.

    :param angle: a single angle in randians.
    :return: the angle converted to integer degrees, unless the angle was
        -999 or nan.

    """
    return where(isnan(angles) | (angles == -999),
                 -999, degrees(angles)).astype(int)


def clean_angles(angle):
    """Convert radians to degrees, but only if not -999.

    :param angle: a single angle in randians.
    :return: the angle converted to integer degrees, unless the angle was
        -999 or nan.

    """
    if isnan(angle) or int(angle) == -999:
        return -999
    else:
        return int(degrees(angle))


def prettyprint_timerange(t0, t1):
    """Pretty print a time range."""

    duration = t1 - t0
    if (duration.seconds > 0 or t0.second > 0 or t0.minute > 0 or t0.hour > 0):
        timerange = '%s %s' % (t0, t1)
    elif duration.days == 1:
        timerange = str(t0.date())
    else:
        timerange = '%s %s' % (t0.date(), t1.date())

    timerange = timerange.replace('-', '').replace(' ', '_').replace(':', '')
    return timerange


def get_lightning_path(date):
    """Return a reference to the raw data file on a specified date"""

    dir = os.path.join(settings.DATASTORE_PATH, '%d/%d' % (date.tm_year,
                                                           date.tm_mon))
    name = os.path.join(dir, '%d_%d_%d.h5' % (date.tm_year, date.tm_mon,
                                              date.tm_mday))
    return name


class FakeReconstructionsTable(object):

    """Used as standin for a missing reconstruction table

    Supports indexing with a list of values.
    It returns a dictionary with 'column' of values.
    The length is equal to the length of the input.

    """

    def __getitem__(self, key):
        """Get a fake 'array' of reconstructions

        :param key: a list of values (usually row indices).
        :return: a dictionary with zenith and azimuth as keys
                 and arrays of -999 with length equal to key as values.

        """
        arr = empty(len(key))
        arr.fill(-999)
        return {'zenith': arr, 'azimuth': arr}
