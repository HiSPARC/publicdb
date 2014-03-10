""" Script to generate some graphs for Jos Steijger

    This script was used to generated some graphs used in a mail exchange
    with Jos Steijger.

"""
import os
import tables
import datetime
import pylab

from hisparc.publicdb import download_data


def make_hist(data, bins, title, xlim=None):
    pylab.figure()
    for x in data:
        pylab.hist(x, bins=bins, log=True, histtype='step')
    pylab.title(title)
    pylab.xlabel('pulse height (raw ADC values)')
    pylab.ylabel('count')
    if xlim:
        pylab.xlim(xlim)

if __name__ == '__main__':
    if os.path.exists('jos.h5'):
        data = tables.openFile('jos.h5', 'r')
    else:
        data = tables.openFile('jos.h5', 'w')
        download_data(data, '/hisparc/s501', station_id=501,
                      start=datetime.datetime(2009, 1, 3),
                      end=datetime.datetime(2009, 1, 11))
        download_data(data, '/hisparc/s505', station_id=505,
                      start=datetime.datetime(2009, 1, 3),
                      end=datetime.datetime(2009, 1, 11))

    ph = [x['pulseheights'] for x in data.root.hisparc.s501.events]
    twohigh = zip(*[x for x in ph if (x >= 123).tolist().count(True) >= 2])
    #threelow = zip(*[x for x in ph if (x >= 53).tolist().count(True) >= 3])
    #twoscint = zip(*[x[:2] for x in ph if (x[:2] >= 123).tolist().count(True) >= 2])

    make_hist(twohigh, bins=range(0, 2000, 20),
              title="Trigger: at least two high (20 ADC values per bin)")
    make_hist(twohigh, bins=range(0, 2000, 1),
              title="Trigger: at least two high (1 ADC values per bin)")
    make_hist(twohigh, bins=range(0, 2000, 1),
              title="Trigger: at least two high (1 ADC values per bin)",
              xlim=(0, 200))

    pylab.show()
