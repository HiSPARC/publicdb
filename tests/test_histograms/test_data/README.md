How to create the test data
===========================


Notes on recreating `datastore/2017/1/2017_1_1.h5`
--------------------------------------------------

This test data is simply 5 minutes of real data from station 501
downloaded from the raw data via the Public Database.
Because the download script downloads all blobs those need to be removed
after downloading, and the file repacked otherwise you are left with
80MB of data. This can be done using the following script:

```python
import os
import tables
from datetime import datetime
from sapphire.publicdb import download_data

with tables.open_file('temp_data.h5', 'w') as data:
    download_data(data, '/hisparc/cluster_amsterdam/station_501', 501, datetime(2017, 1, 1),
                  datetime(2017, 1, 1, 0, 5), get_blobs=True)
    max_trace_id = data.root.hisparc.cluster_amsterdam.station_501.events.col('traces').max()
    data.root.hisparc.cluster_amsterdam.station_501.blobs.truncate(max_trace_id + 1)

try:
    os.makedirs('datastore/2017/1/')
except FileExistsError:
    pass
```

```bash
ptrepack --complevel 9 --complib blosc temp_data.h5 datastore/2017/1/2017_1_1.h5
rm -f temp_data.h5
```
