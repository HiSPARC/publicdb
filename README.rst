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

Besides all the Python packages that will need to be installed next you
also need the HDF5 libraries.  These are required to work with the h5 data
files and to install the python tables package.  If your system does not
provide a recent versions of these libraries, download the source::

    $ wget http://www.hdfgroup.org/ftp/HDF5/prev-releases/hdf5-1.8.9/src/hdf5-1.8.9.tar.gz
    $ tar xvzf hdf5-1.8.9.tar.gz
    $ cd hdf5-1.8.9
    
Then apply this patch::

    --- CMakeLists.txt (revision 22471)
    +++ CMakeLists.txt (working copy)
    @@ -884,7 +884,7 @@
    -        ${HDF5_SOURCE_DIR}/release_docs/Using_CMake.txt
    +        ${HDF5_SOURCE_DIR}/release_docs/USING_CMake.txt

And continue the build::
             
    $ ./configure --prefix=/usr/local
    $ make
    $ make install
    $ ldconfig

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

    $ mkvirtualenv --distribute publicdb

where you can replace *publicdb* with any name you like.  If the
environment is not already automatically activated, do that with::

    $ workon publicdb


Python Packages
^^^^^^^^^^^^^^^

We will now populate this environment with all prerequisites.  To
duplicate the environment used while writing this documentation, use the
following instructions, including version numbers.  To install the latest
versions of the software, drop the `==<version>` part.  For example, you
can install ipython 0.13.1 using::

    $ pip install ipython==0.13.2

Alternatively, install the latest version with::

    $ pip install ipython

The complete requirements and installation instructions are::

    $ pip install ipython

    $ pip install numpy

    $ pip install Cython
    $ pip install numexpr
    $ pip install tables

    $ pip install recaptcha-client

    $ pip install Django
    $ pip install South
    $ pip install docutils

    $ pip install progressbar
    $ pip install mock
    $ pip install scipy
    $ pip install matplotlib
    $ pip install https://github.com/hisparc/sapphire/zipball/master

You now have all the prerequisites for running the publicdb django app.
For reference, the results from `pip freeze`::

    $ pip freeze
    Cython==0.19.1
    Django==1.5.1
    South==0.8.1
    distribute==0.6.34
    docutils==0.10
    ipython==0.13.2
    matplotlib==1.2.1
    mock==1.0.1
    numexpr==2.1
    numpy==1.7.1
    progressbar==2.3
    recaptcha-client==1.0.6
    sapphire==0.9.2b
    scipy==0.12.0
    tables==3.0.0
    wsgiref==0.1.2

Note for Mac OS X users: python has trouble detecting the default locale.
Before continuing, it's best to type this into your terminal::

    $ export LC_ALL=en_US.UTF-8

Navigate to the `django_publicdb` folder and populate (and migrate) a test
database with::

    $ cp settings-develop.py settings.py
    $ ./manage.py syncdb
    $ ./manage.py migrate


Hints for running a development publicdb server
-----------------------------------------------

First, we assume that you're working in the virtualenv you created
previously::

    $ workon publicdb

In order to create a tiny copy of the datastore for development purposes,
do::

    $ python scripts/download_test_datastore.py

To generate the histograms for the downloaded data::

    $ python scripts/hisparc-update.py

You can start the Django development server from inside the Django app
directory (the one containing your settings.py) with::

    $ ./manage.py runserver


Deployment
----------

We recently ditched Apache.  We've had problems with mod_wsgi before and
now Apache proper (or mod_wsgi) was breaking our streaming HTTP response
for downloading the event summary data.  So, finally, we're moving to a
modern solution: `uWSGI <http://projects.unbit.it/uwsgi/>`_.  We've taken
the opportunity to clean up a few things.

Following the FHS, we've deployed the public database code in ``/srv``.
We've created a ``publicdb`` directory containing a virtualenv, git
repository and static files.  The ``hisparc`` group has write access and
using ACLs all newly-created files have group write permissions.  As
root::

    # cd /srv
    # mkdir publicdb
    # chown hisparc.hisparc publicdb
    # chmod g+rwx publicdb

To set a default ACL entry granting group write permissons for all files,
type::

    # setfacl -m d:g::rwx publicdb

Now we can drop root privileges and continue as a regular user, which must
be a member of the ``hisparc`` group.  To clone the publicdb git
repository::

    $ cd publicdb
    $ git clone https://github.com/HiSPARC/publicdb.git www

Unfortunately, due to some unknown quirk, ``git clone`` does not respect
the default ACL entry, so we have to grant group write permissions::

    $ chmod g+w www

Then, create the directory holding the static files::

    $ mkdir static

Create a python virtualenv for the web server::

    $ virtualenv --distribute publicdb_env

Be sure to activate the virtualenv whenever you work on the web server::

    $ source /srv/publicdb/publicdb_env/bin/activate

Or, if you're stuck with a csh::

    $ source /srv/publicdb/publicdb_env/bin/activate.csh

At this point we've followed the python package install instructions as
documented in the `Python Packages`_ section.  Furthermore, we need some
additional packages to install the uWSGI server, and access the MySQL
database::

    $ pip install uwsgi uwsgitop
    $ pip install mysql-python

At this point it is necessary to modify Django's ``settings.py`` for
production.  We've used ``settings-develop.py`` as a starting point.  The
``settings.py`` file is added to ``.gitignore``, so you don't have to
worry about accidentally committing sensitive information.  To deploy the
static files::

    $ cd /srv/publicdb/www/django_publicdb/
    $ ./manage.py collectstatic

This has to be repeated whenever a commit introduces new or changed static
files.

We've installed `supervisor <http://supervisord.org>`_ to manage the uWSGI
process.  We've added the following program entry::

    [program:uwsgi]
    command=/srv/publicdb/publicdb_env/bin/uwsgi --ini /srv/publicdb/www/uwsgi.ini
    stopsignal=INT

The uWSGI config file currently in production::

    [uwsgi]
    master = True
    master-as-root = True
    uid = hisparc
    gid = hisparc

    processes = 9
    threads = 4

    http = 0.0.0.0:80
    stats = 127.0.0.1:9191

    chdir = /srv/publicdb/www/django_publicdb/
    home = /srv/publicdb/publicdb_env/
    pythonpath = ..
    env = DJANGO_SETTINGS_MODULE=django_publicdb.settings
    module = django.core.handlers.wsgi:WSGIHandler()
    static-map = /media/static=/srv/publicdb/static
    static-map = /media/raw_data=/var/www/html/media/raw_data
    static-map = /media/jsparc=/srv/publicdb/jsparc

    auto-procname = True
    pidfile = /var/run/uwsgi.pid
    logto = /var/log/uwsgi.log
    logfile-chown = True
    touch-reload = /tmp/uwsgi-reload.me

    route-uri = ^/django/(.*)$ redirect-permanent:/$1

And the cron job to do a nightly run of data processing::

    0 4 * * * hisparc /srv/publicdb/publicdb_env/bin/python /srv/publicdb/www/scripts/hisparc-update.py
