.. include:: subst.inc

API Tutorial
============

The |hisparc| |api| (Application Programming Interface) simplifies
metadata access from other applications. In this tutorial, we'll give
some examples of how this data can be accessed and used with Javascript
(`jQuery <http://www.jquery.com/>`_) and `Python
<http://www.python.org>`_. We'll show you how to do some neat things.
How can you get a list of all |hisparc| stations in Denmark? What is the
position of station 201? Which stations had data on 20 October 2010? How
does the number of measured events change during a few weeks? This
tutorial will give you an overview of some of possibilities with the
|hisparc| |api|. For details on all available classes and methods,
please see the :doc:`api`.

.. note::
    We'll require you to know some basic programming, i.e. to understand
    what an :code:`if` statement is and :code:`for` loop does. If you
    are new to coding you can try a tutorial online, for instance
    `Codeacademy <http://www.codecademy.com/>`_, we recommend learning
    Python or jQuery.


First look
----------

First we will just look at what this |api| is. The |api| can be accessed
via the internet by opening urls. Instead of a website you get data as a
response. This data is formatted as a JSON (JavaScript Object Notation),
this format can be understood by many programming languages.

To see what options the |api| has we will look at it in a browser. Open
the following link in your browser (this will not work in Internet
Explorer): `http://data.hisparc.nl/api/ <http://data.hisparc.nl/api/>`_.

You should now see some text, like this:

.. code-block:: javascript

    {"base_url": "http://data.hisparc.nl/api/",
     "clusters": "clusters/",
     "clusters_in_country": "countries/{country_id}/",
     "configuration": "station/{station_id}/config/{year}/{month}/{day}/",
     "countries": "countries/",
     "has_data": "station/{station_id}/data/{year}/{month}/{day}/",
     ...
     "subclusters_in_cluster": "clusters/{cluster_id}/"}

This is the JSON, it is a dictionary (indicated by the :code:`{` and
:code:`}` enclosing brackets): an object which has keys and values. Each
key (:code:`"clusters"`, :code:`"has_data"`) refers to a value
(:code:`"clusters/"`,
:code:`"station/{station_id}/data/{year}/{month}/{day}/"`).


Cluster list
^^^^^^^^^^^^

This tells us that if we want a list of all clusters we need to use the
clusters option by appending :code:`"clusters/"` to the base url,
resulting in the following:
`http://data.hisparc.nl/api/clusters/ <http://data.hisparc.nl/api/clusters/>`_.

With this result:

.. code-block:: javascript

    [{"name": "Amsterdam",
      "number": 0},
     {"name": "Utrecht",
      "number": 1000},
     ...
     {"name": "Karlsruhe",
      "number": 70000}]

This JSON is a list (indicated by the :code:`[` and :code:`]` enclosing
brackets) of dictionaries, one for each cluster. Each dictionary
contains the name and number of a cluster. This way information about
the network of stations can be retrieved.


Javascript example
------------------

The following code example will generate a webpage which will use the
|api| to get an up-to-date list of stations. It will then show a
drop-down menu from which a station can be selected, once you have
chosen a station you can click the :code:`Get info` button to make
Javascript get the station information. To try this you can either use
this example page: `jsFiddle <http://jsfiddle.net/NCWXq/2/>`_ or create
your own HTML file with this code:

.. code-block:: html

    <html>
    <head>
    <script src="http://code.jquery.com/jquery-1.11.1.min.js"></script>
    <script>
        $(function() {
            // Get an up-to-date list of HiSPARC stations
            $.getJSON(
                'http://data.hisparc.nl/api/stations/',
                function(data) {
                    // Create the drop-down menu
                    var select = $('<select>');
                    var id, name;
                    for (var i in data) {
                        id = data[i].number;
                        name = data[i].name;
                        select.append($('<option>').attr('value', id).text(id + ' - ' + name));}
                    $('#station_list').append(select);});

            // Attach a function to the Get info button
            $('#get_station').on('click', function() {
                var id = $('#station_list').find('select').val();
                // Get info for selected station and display it in a nice way
                $.getJSON('http://data.hisparc.nl/api/station/' + id + '/',
                          function(data) {
                              $('#station_info').text(JSON.stringify(data, undefined, 4));
                          });
                });
            });
    </script>
    </head>
    <body style="font-family: sans-serif;">
        <h2>Station info</h2>
        <p id="station_list">Choose a station: </p>
        <input type="submit" id="get_station" value="Get info">
        <pre id="station_info"></pre>
    </body>
    </html>


Python example
--------------

In this example we will use several standard Python libraries and the
popular plotting library `matplotlib <http://matplotlib.org>`_ (pylab).
We start by importing the required libraries, one to get data from the
urls, one to make working with dates easy and the plotting library. Then
define the start values and perpare two empty lists in which the data
can be placed. Then a while loop is used to loop over all days between
datum and end_datum, reading each corresponding url. Finally a plot is
made, setting the dates against their values.

Start Python and type (or copy/paste without the :code:`>>> `) the
following lines of code:

.. code-block:: python

    >>> from urllib2 import urlopen
    >>> from datetime import date, timedelta
    >>> from pylab import plot, show
    >>> id = 501
    >>> datum = date(2010, 10, 1)
    >>> end_datum = date(2011, 2, 1)
    >>> base = 'http://data.hisparc.nl/api/station/%d/num_events/%d/%d/%d'
    >>> events = []
    >>> dates = []
    >>> while datum < end_datum:
    ...     url = urlopen(base % (id, datum.year, datum.month, datum.day))
    ...     events.append(url.read())
    ...     dates.append(datum)
    ...     datum += timedelta(days=1)
    ...
    >>> step(dates, events)
    >>> show()


SAPPHiRE
^^^^^^^^

The HiSPARC Python framework SAPPHiRE includes an API module. This module
simplifies access to the API. See the SAPPHiRE documentation for more
information:
`http://docs.hisparc.nl/sapphire/ <http://docs.hisparc.nl/sapphire/>`_.
