HiSPARC Public Database README
==============================


Overview
--------

The HiSPARC Public Database is a Django application which stores derived
data and displays it for public use.  It exposes an API to download raw
detector data from the datastore, as well as an API to participate in
analysis sessions.


Setting up a personal development environment
---------------------------------------------

We recommend you use virtualenv (with virtualenvwrapper) to set up an
isolated python environment.  Throughout this document we assume you have
pip installed and we prefer that above easy_install.  You can install pip
with::

    $ easy_install pip

And virtualenv/virtualenvwrapper with::

    $ pip install virtualenvwrapper

Add this line to your login file (.bashrc) and restart your Terminal::

    source [PATHTO]/virtualenvwrapper.sh

Create a clean environment with::

    $ mkvirtualenv publicdb

where you can replace *publicdb* with any name you like.  If the
environment is not already automatically activated, do that with::

    $ workon publicdb

We will now populate this environment with all prerequisites.  To
duplicate the environment used while writing this documentation, use the
following instructions, including version numbers.  To install the latest
versions of the software, drop the `==<version>` part.  For example, you
can install ipython 0.12.1 using::

    $ pip install ipython==0.12.1

Alternatively, install the latest version with::

    $ pip install ipython

The complete requirements and installation instructions are::

    $ pip install ipython==0.12.1

    $ pip install Cython==0.16
    $ pip install numpy==1.6.2

    $ pip install numexpr==2.0.1
    $ pip install tables==2.3.1

    $ pip install recaptcha-client==1.0.6

    $ pip install Django==1.4
    $ pip install South==0.7.3

You now have all the prerequisites for running the publicdb django app.
For reference, the results from `pip freeze`::

    $ pip freeze
    Cython==0.16
    Django==1.4
    South==0.7.3
    ipython==0.12.1
    numexpr==2.0.1
    numpy==1.6.2
    recaptcha-client==1.0.6
    tables==2.3.1
    wsgiref==0.1.2

Navigate to the `django_publicdb` folder and populate (and migrate) a test
database with::

    $ ./manage.py syncdb
    $ ./manage.py migrate


Hints for running a development publicdb server
-----------------------------------------------

First, we assume that you're working in the virtualenv you created
previously::

    $ workon publicdb

In order to create a tiny copy of the datastore for development purposes,
do::

    $ cd scripts/
    $ python download_test_datastore.py

You can start the Django development server from inside the Django app
directory (the one containing your settings.py) with::

    $ ./manage.py runserver

The settings point to a temporary mediaroot in the source tree, and a HTTP
server running on port 8008 to serve the files.  If you want to serve
files from that directory using a development server, change to the
directory *above* the ``mediaroot`` directory and do::

    $ python -m SimpleHTTPServer 8008
