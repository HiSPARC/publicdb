from django.http import HttpResponse
from django.template import loader, Context
from django.conf import settings

import os
import tables
import datetime
import urlparse
import tempfile

from SimpleXMLRPCServer import SimpleXMLRPCDispatcher
dispatcher = SimpleXMLRPCDispatcher()

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
    :param date: retrieve events from this day

    """

    date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

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

    dir = os.path.join(settings.DATASTORE_PATH, '%d/%d' % (date.year,
                                                           date.month))
    name = os.path.join(dir, '%d_%d_%d.h5' % (date.year, date.month,
                                              date.day))
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
