""" Search for coincidences in a subcluster

    This script is a small demonstration which shows how to download data
    from all detectors in a subcluster, in this case the Science Park in
    Amsterdam, and search for coincidences.

    In this script, we only search for coincidences which occured during
    one hour.  This is only to show that datetime can also be used to
    specify time, not only a date.  It is very well possible to search for
    coincidences during the complete day.  The time that will cost may
    surprise you.

    Just replace the lines:

                                 start=datetime.datetime(2009, 2, 24, 12),
                                 stop=datetime.datetime(2009, 2, 24, 13),

    with:

                                 start=datetime.datetime(2009, 2, 24),
                                 stop=datetime.datetime(2009, 2, 25),

    and you're set.
"""

import tables
import datetime
from hisparc.publicdb import download_data
from hisparc.analysis import coincidences
import time

if __name__ == '__main__':
    data = tables.openFile('test.h5', 'w')

    t0 = time.time()
    for station in range(501, 506):
        download_data(
            data, '/hisparc/station' + str(station), station_id=station,
            start=datetime.datetime(2009, 2, 24, 12),
            end=datetime.datetime(2009, 2, 24, 13))

    t1 = time.time()
    coincidences, timestamps = coincidences.search_coincidences(
                                    data,
                                    ['/hisparc/station501',
                                     '/hisparc/station502',
                                     '/hisparc/station503',
                                     '/hisparc/station504',
                                     '/hisparc/station505'],
                                    shifts=[None, None, -15, None, None])
    t2 = time.time()
    print 'Download: %f (%.1f%%)' % (t1 - t0, 100 * (t1 - t0) / (t2 - t0))
    print 'Processing: %f (%.1f%%)' % (t2 - t1,
                                       100 * (t2 - t1) / (t2 - t0))
    print 'Total:', t2 - t0
