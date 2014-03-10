""" Read data from a raw data file and save timestamps as CSV

    This example script reads event data from a raw data file, extracts
    the timestamps, reformats them in date, time strings and saves them,
    along with nanoseconds, into a CSV file.

    This script was used to provide high school students with detector
    data for their analysis.
"""

import tables
import datetime
import csv
import zlib
import numpy as np

def get_traces(groupnode, traces_idx):
    """Get traces from groupnode and reference"""

    traces_array = groupnode.traces
    traces = []
    for idx in traces_idx:
        trace = zlib.decompress(traces_array[idx])
        trace = [int(x) * -.57 + 114.0 for x in trace.split(',')[:-1]]
        #trace = ','.join(['%d' % x for x in trace])
        traces.append(trace)

    return traces

def write_event_frequency():
    # Read data from file
    with tables.openFile('ettyhillesum.h5', 'r') as datafile:
        data = [x['timestamp'] for x in
                datafile.root.hisparc.ettyhillesum.events]

    # Unix timestamps don't do leap seconds, they just freeze.  So, every
    # hour is 3600 seconds.  We want start and end to be on the hour.
    start = data[0] - data[0] % 3600
    end = data[-1] - data[-1] % 3600 + 3600
    hist, bin_edges = np.histogram(data, bins=np.arange(start, end, 3600))

    datalist = []
    for bin, value in zip(bin_edges, hist):
        dt = datetime.datetime.fromtimestamp(bin)
        dt = dt.ctime()
        datalist.append((dt, value))

    # Write data into a CSV file
    with open('ettyhillesum-freq.csv', 'w') as file:
        writer = csv.writer(file, dialect='excel-tab')
        writer.writerows(datalist)

def write_strong_events():
    # Read data from file
    with tables.openFile('ettyhillesum.h5', 'r') as datafile:
        group = datafile.root.hisparc.ettyhillesum

        data = [(x['pulseheights'], x['traces']) for x in group.events if
                min(x['pulseheights']) > (500 / .57)][:10]

        datalist = []
        for ph, idx in data:
            traces = get_traces(group, idx)
            datalist.append((ph, traces))

    for num, event in enumerate(datalist):
        with open('ettyhillesum-event-%02d.csv' % num, 'w') as file:
            writer = csv.writer(file, dialect='excel-tab')
            for sample, values in enumerate(zip(*event[1])):
                values = ['%d' % x for x in values]
                row = [sample * 2.5]
                row.extend(values)
                writer.writerow(row)


if __name__ == '__main__':
    write_event_frequency()
    write_strong_events()
