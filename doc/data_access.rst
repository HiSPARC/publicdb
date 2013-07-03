.. include:: subst.inc

Data access
===========

There are several ways in which the |hisparc| data can be accessed:

- Via the Public database Download Form
- Via Python using the |sapphire| framework (see `SAPPHiRE Tutorial
  <http://docs.hisparc.nl/sapphire/tutorial.html#downloading-and-accessing
  -hisparc-data>`_)

On this page the second method is explained and examples are given. To
access metadata, like a list of all stations or information about a
specific station see the :doc:`api_tutorial`.


Download Form
-------------

When looking at the data page for a station (i.e. `Kaj Munk College
<http://data.hisparc.nl/show/stations/202/>`_), you will see a 'Download
event summary data' link on the right. When this link is clicked you
will be taken to the `Data Download Form
<http://data.hisparc.nl/data/download>`_. On this page you can select
the station, the start and end date for which you want to download the
data.

When you click the Submit button without checking the checkbox to
Download, the data should (Firefox always download the data) show up in
your browser window. If you check the Download box the data will be
downloaded to your PC as a csv file. The filename will contain the
station number and the dates selected.

This csv file can be read by many programs, like Excel.


Downloading via Python
----------------------

This is an example of how to download the data from the Public database
in Python. In this example we will download 1 hour of data for station
202 on July 2, 2013.

First load the required libraries (requires the numpy package).

.. code-block:: python

    >>> from urllib2 import urlopen
    >>> from urllib import urlencode
    >>> from datetime import datetime
    >>> from csv import reader
    >>> from StringIO import StringIO
    >>> from numpy import genfromtxt

Then define the url and place the start and end datetime in the query.

.. note::

    Do not pass the query to the urlopen 'data' argument because that
    changes the request into a *POST* request, but you need a *GET*
    request.

.. code-block:: python

    >>> url = 'http://data.hisparc.nl/data/202/events'
    >>> start = str(datetime(2013, 7, 2, 11, 0))
    >>> end = str(datetime(2013, 7, 2, 12, 0))
    >>> query = urlencode({'download': False, 'start': start,'end': end})
    >>> full_url = url + '?' + query

Download the data and store it in a variable

.. code-block:: python

    >>> data = urlopen(full_url).read()

Now use numpy to convert the data from csv to a numpy array.

.. code-block:: python

    >>> format = [('date', 'datetime64[D]'), ('time', '|S8'),
                  ('timestamp', 'uint32'), ('nanoseconds', 'uint32'),
                  ('pulseheights', '4int16'), ('integrals', '4int16'),
                  ('n1', 'float32'), ('n2', 'float32'),
                  ('n3', 'float32'), ('n4', 'float32'),
                  ('t1', 'float32'), ('t2', 'float32'),
                  ('t3', 'float32'), ('t4', 'float32')]
    >>> a = genfromtxt(StringIO(data), delimiter="\t", dtype=format)
    >>> print a[0]
    (datetime.date(2013, 7, 2), '11:00:02', 1372762802L, 466307811L,
     [78, 798, -1, -1], [535, 10882, -1, -1],
     0.14720000326633453, 3.854599952697754, -1.0, -1.0,
     345.0, 12.5, -1.0, -1.0)
