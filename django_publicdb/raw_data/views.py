from django.http import HttpResponse
from django.template import loader, Context
from django.conf import settings
from django.shortcuts import render_to_response, redirect

import csv
import datetime
import os
import time
import tables
import datetime
import urlparse
import tempfile
import StringIO
import numpy as np
import zlib

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
dispatcher = SimpleXMLRPCDispatcher()

from forms import DataDownloadForm
from inforecords.models import Station


ADC_THRESHOLD = 20
ADC_TIME_PER_SAMPLE = 2.5


def call_xmlrpc(request):
    """Dispatch XML-RPC requests."""
    if request.method == 'POST':
        # Process XML-RPC call
        response = HttpResponse(mimetype='text/xml')
        response.write(dispatcher._marshaled_dispatch(request.raw_post_data))
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

def download_form(request):
    if request.method == 'POST':
        form = DataDownloadForm(request.POST)
        if form.is_valid():
            station_id = form.cleaned_data['station']
            start_date = form.cleaned_data['start_date']
            end_date = form.cleaned_data['end_date']
            get_timings = form.cleaned_data['get_timings']
            return redirect(download_data, station_id, start_date,
                            end_date)
    else:
        form = DataDownloadForm()

    return render_to_response('rawdata/data_download_form.html', {
        'form': form,
    })

def download_data(request, station_id, start_date, end_date):
    generator = generate_station_data_between_dates(station_id,
                                                    start_date, end_date)
    filename = "data_%s_%s_%s.csv" % (station_id, start_date, end_date)

    response = HttpResponse(generator, mimetype='text/csv')
    response['Content-Disposition'] = 'attachment; filename=%s' % filename
    return response

def generate_station_data_between_dates(station_id, start_date, end_date):
    station = Station.objects.get(number=station_id)
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()

    date = start_date
    while date < end_date:
        try:
            yield get_station_data_for_date(station, date)
        except (tables.NoSuchNodeError, IOError):
            pass
        date += datetime.timedelta(days=1)

def get_station_data_for_date(station, date):
    data = get_datafile_for_date(date)
    events, blobs = get_event_tables_for_station(data, station)
    csv_data = events_as_csv(events, blobs)

    data.close()
    return csv_data

def get_datafile_for_date(date):
    datastore = settings.DATASTORE_PATH
    filename = '%s_%s_%s.h5' % (date.year, date.month, date.day)
    path = os.path.join(datastore, str(date.year), str(date.month), filename)
    return tables.openFile(path, 'r')

def get_event_tables_for_station(data, station):
    group = data.getNode('/hisparc', 'cluster_%s/station_%d' %
                        (station.cluster.name.lower(), station.number))
    return group.events, group.blobs

def events_as_csv(events, blobs):
    output = StringIO.StringIO()
    writer = csv.writer(output, delimiter='\t')

    for event in events:
        datetime_string = time.asctime(time.gmtime(event['timestamp']))
        detector_timings = get_timings_from_traces(event, blobs)
        writer.writerow(flatten([datetime_string, event['timestamp'],
                         event['nanoseconds'], event['ext_timestamp'],
                         event['n_peaks'], event['pulseheights'],
                         event['integrals'], detector_timings]))
    return output.getvalue()

def flatten(list_of_objects):
    result = []
    for element in list_of_objects:
        if (isinstance(element, tuple) or isinstance(element, list) or
            isinstance(element, np.ndarray)):
            result.extend(flatten(element))
        else:
            result.append(element)
    return result

def get_timings_from_traces(event, blobs):
    traces = get_traces(blobs, event)
    return [reconstruct_time_from_trace(trace) for trace in traces]

def get_traces(traces_table, event):
    """Retrieve traces from table and reconstruct them"""

    if type(event) != list:
        idxs = event['traces']
    else:
        idxs = event

    traces = []
    for idx in idxs:
        trace = zlib.decompress(traces_table[idx]).split(',')
        if trace[-1] == '':
            del trace[-1]
        trace = np.array([int(x) for x in trace])
        traces.append(trace)
    return traces

def reconstruct_time_from_trace(trace):
    """Reconstruct time of measurement from a trace"""

    t = trace[:100]
    baseline = np.mean(t)

    trace = trace - baseline
    threshold = ADC_THRESHOLD

    value = np.nan
    for i, t in enumerate(trace):
        if t >= threshold:
            value = i
            break

    if value is not np.nan:
        return value * ADC_TIME_PER_SAMPLE
    else:
        return -999
