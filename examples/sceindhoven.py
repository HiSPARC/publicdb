""" Read data from a raw data file and save timestamps as CSV

    This example script reads event data from a raw data file, extracts
    the timestamps, reformats them in date, time strings and saves them,
    along with nanoseconds, into a CSV file.

    This script was used to provide a high school student with detector
    data for his analysis.
"""

import tables
import datetime
import csv

if __name__ == '__main__':
    # Read data from file
    with tables.openFile('sceindhoven.h5', 'r') as datafile:
        data = [(x['timestamp'], x['nanoseconds'], x['pulseheights']) for
                x in datafile.root.hisparc.sceindhoven.events]

    # Reformat data
    datalist = []
    for timestamp, nanoseconds, pulseheights in data:
        # Format timestamps into date and time strings
        d_t = datetime.datetime.fromtimestamp(timestamp)
        date = d_t.date().isoformat()
        time = d_t.time().isoformat()
        # Convert pulseheights into mV units (only 2 master channels)
        pulseheights = [x * .57 for x in pulseheights[:2]]
        ph1, ph2 = pulseheights
        # Save data values
        datalist.append((date, time, nanoseconds, ph1, ph2))

    # Write data into a CSV file
    with open('sceindhoven.csv', 'w') as file:
        writer = csv.writer(file)
        writer.writerows(datalist)
