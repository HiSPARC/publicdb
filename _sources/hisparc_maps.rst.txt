.. include:: subst.inc

HiSPARC maps
============

Each |hisparc| station is equipped with a GPS antenne. This GPS is used
to for time synchronization between stations and to determine the exact
location of each station. All these locations are stored in our
database. The GPS positions can be found on the data pages of stations,
via the API (:doc:`api`) and in the raw data.


Map
---

Using the `Leafet <https://leafletjs.com>`_ library with `CARTO
<https://carto.com>`_ maps tiles (based on `OpenStreetMap
<https://www.openstreetmap.org>`_ data) we are able to visualize the
detector network by showing the locations of the stations on a map.

Here is an overview of the network: `Stations on map
<https://data.hisparc.nl/show/stations_on_map/>`_


Station info
^^^^^^^^^^^^

When you click on a station marker a popup will show information about
that station, its name and cluster. If the station has data the name of
the station will be a link to its data page.


Status
^^^^^^

The stations on the map can have one of 4 colors to indicate the current
status of that station.

- Green: when a station is operating properly
- Yellow: it is responding to the server but has a problem
- Red: it is completely unresponsive (offline)
- Gray: it is is no longer active or the status can't be determined.


Embedding
---------

On several public database pages a map is embedded to show the station
location or provide an overview of multiple stations. Moreover, maps are
also used on our main website to give an overview of the station
organization and clustering (e.g. `Bristol
<https://www.hisparc.nl/over-hisparc/organisatie/bristol-uk/>`_, `Science
Park
<https://www.hisparc.nl/over-hisparc/organisatie/amsterdam/science-park/>`_
). This is accomplished by placing an iframe on those pages that
shows another page which only has the map as its content. Example code:

.. code-block:: html

    <iframe src="https://data.hisparc.nl/maps/Netherlands/Amsterdam/Science%20Park/"
            scrolling="no" frameborder="0" width="600" height="300"></iframe>

Result:

.. raw:: html

    <div style="margin-top:10px;">
      <iframe src="https://data.hisparc.nl/maps/Netherlands/Amsterdam/Science%20Park/"
            scrolling="no" frameborder="0" width="600" height="300"></iframe>
    </div>


Syntax
^^^^^^

To show a map of a specific region or location, use the syntax explained
here. First start with the base url::

    https://data.hisparc.nl/maps/

When no extra options are given the page zooms and positions the map
such that all stations fit in the window. But you can also focus on a
specific region or station. Several levels of regions are possible::

    https://data.hisparc.nl/maps/[Country]/[Cluster]/[Subcluster]/
    https://data.hisparc.nl/maps/[Station number]/

An overview of countries, clusters and subclusters can be found on
https://data.hisparc.nl/ . First you can choose to focus on a Country:

- https://data.hisparc.nl/maps/Netherlands/
- https://data.hisparc.nl/maps/Denmark/

Then focus more closely on a cluster, note that you also need to give
the country:

- https://data.hisparc.nl/maps/Netherlands/Enschede/
- https://data.hisparc.nl/maps/Netherlands/Utrecht/
- https://data.hisparc.nl/maps/United%20Kingdom/Bristol/

And to focus on a subcluster, also specifying the country and cluster:

- https://data.hisparc.nl/maps/Netherlands/Amsterdam/Zaanstad/
- https://data.hisparc.nl/maps/Netherlands/Enschede/Enschede/

Finally you can also focus on one specific station by simply giving its
station number:

- https://data.hisparc.nl/maps/8005/
- https://data.hisparc.nl/maps/8103/
