""" Import and plot some KVI data

    This script is a small demonstration which shows how to download some
    data from one particular detector, in this case 4001 at KVI, and make
    a simple pulse height histogram.
"""

import tables
import datetime
from hisparc.publicdb import download_data
import pylab

if __name__ == '__main__':
    # Open data file and download data
    data = tables.openFile('kvi.h5', 'w')
    download_data(data, '/hisparc/kvi', station_id=4001,
                  start=datetime.datetime(2009, 11, 23),
                  end=datetime.datetime(2009, 11, 24))

    # Fetch pulseheights...
    ph = [x['pulseheights'] for x in data.root.hisparc.kvi.events]
    # ...and rearrange
    ph = zip(*ph)
    # ...and drop detectors 3 and 4 (slave not attached)
    ph = ph[:2]

    # Convert to mV
    ph = [[x * .57 for x in det] for det in ph]

    # Bin pulseheights of detector 1 and 2
    pylab.hist(ph[0], bins=100, range=[0, 2000], histtype='step')
    pylab.hist(ph[1], bins=100, range=[0, 2000], histtype='step')
    pylab.axis('auto')
    pylab.xlabel('pulseheight (mV)')
    pylab.ylabel('count')
    pylab.title('Pulseheight histogram (4001, kvi)')
    pylab.show()
