HiSPARC Public Database README
==============================


Overview
--------

The HiSPARC Public Database is a Django application which stores derived
data and displays it for public use.  It exposes an API to download raw
detector data from the datastore, as well as an API to participate in
analysis sessions.

.. contents:: Table of Contents

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

We recommend you to use virtualenv (with virtualenvwrapper) to set up an
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


Testing
-------

It is imperative (or good practice) that the 'master' branch (main branch) is
always in a state such that it can be checked out and run without any problems.
Automated testing is a tool to check whether your modifications work as
expected, don't break the functionality or (re-)introduce new bugs.

When new features are added, tests should be added for it as well. There are two
ways to do this. The first way is to write the tests before the implementation
is done. The second way is the reverse: first write the implementation and then
the tests. These two ways are at the extremes of a spectrum and the usual
approach lies somewhere in the middle.

When tests are written, please consider the following thoughts:

- Write tests for a specific functionality in an isolated situation
  (`unit testing <https://en.wikipedia.org/wiki/Unit_testing>`_).
- Write tests for a specific functionality in a context interacting with
  other pieces of code (`integration testing <http://en.wikipedia.org/wiki/Integration_testing>`_).
- Give a certain input and check for the expected output or behaviour
  (functional testing). The output does not necessarily have to be the
  returned result of a function, but can be any measurable quantity such as
  the execution time.
- Write tests that explicitly tries to break the functionality. This can be
  done by giving wrong input. Good code has proper input checks and error
  handling.

There are also non-functional tests and they include among other things:

- Compatibility testing
- Performance testing
- Recovery testing
- Security testing
- Stress testing

Running tests
^^^^^^^^^^^^^

Short story
###########

Short story: run tests using the following syntax::

    $ ./manage.py test <application>[[.<test case>].<test>]

where the square brackets denote optional arguments.

For example::

    $ ./manage.py test histograms
    $ ./manage.py test histograms.PulseheightFitTestCase
    $ ./manage.py test histograms.PulseheightFitTestCase.test_jobs_update_pulseheight_fit_normal

Longer story
############

Literature: `Django docs: running tests <https://docs.djangoproject.com/en/1.5/topics/testing/overview/#running-tests>`_

Tests are run by executing the following command::

    $ ./manage.py test <application>

where <application> is the name of the application defined in your settings.py.

For example::

    $ ./manage.py test histograms
    $ ./manage.py test api
    $ ./manage.py test analysissessions
    $ ./manage.py test jsparc

or in one line::

    $ ./manage.py test histograms api analysissessions jsparc

Tests can also be run by executing the next line::

    $ ./manage.py test

however this also include the tests defined in the Django framework itself and
is not recommended.

Tests for an application consists of one or more test cases. Each can be
executed separately using the following syntax::

    $ ./manage.py test <application>.<test case>

For example::

    $ ./manage.py test histograms.PulseheightFitTestCase
    $ ./manage.py test histograms.UpdateAllHistogramsTestCase

Each test case consists of one or more tests. Each can be run separately by the
following expected syntax::

    $ ./manage.py test <application>.<test case>.<test>

For example

    $ ./manage.py test histograms.PulseheightFitTestCase.test_jobs_update_pulseheight_fit_normal

Writing tests
^^^^^^^^^^^^^

Short story
###########

1. Create a 'tests.py' file in your application directory.
2. Define a class inherited from django.test.TestCase.
3. Define a test method with a name starting with "test".

For example a test in the file "publicdb/django_publicdb/dummy/tests.py"::

    from django.test import TestCase

    class DummyTestCase(TestCase):
        def setUp(self):
            pass

        def test_one(self):
            self.assertEqual(1, 1)


Longer story
############

Literature: `Django docs: testing applications <https://docs.djangoproject.com/en/1.5/topics/testing/overview/>`_.

A starting point for writing your own tests would be the existing test suites of
each application of this project. They are located in the file "tests.py" in
each application directory. Each shows different concepts:

- histograms/tests.py: multiple TestCases inherited from a single
  superclass. Includes both unit and integration test cases.
- api/tests.py and jsparc/tests.py: running LiveServerTestCase with urllib2
  as the http client.
- analysissessions/tests.py: running LiveServerTestCase with Firefox as the
  web client. Firefox is automated using Selenium, which provides an API for
  scripting Firefox using python.

A `LiveServerTestCase <https://docs.djangoproject.com/en/1.5/topics/testing/overview/#liveservertestcase>`_
is like executing tests while the publicdb is running from a live http server
(same as ./manage.py runserver).

Fixtures
########

Literature: `Django docs: fixture loading <https://docs.djangoproject.com/en/1.5/topics/testing/overview/#fixture-loading>`_

Some tests require a database loaded with preconfigured sample data. This is
provided via fixtures. Fixtures are data files that can be loaded into a
database. They can be generated by the following command::

    $ ./manage.py dumpdata <application> > application.json

They can be inserted back into the database using::

    $ ./manage.py loaddata application.json

If a fixture needs to be loaded, they have to be specified in the TestCase, for
example::

    from django.test import TestCase

    class DummyTestCase(TestCase):
        fixtures = ["tests_histograms", "tests_inforecords"]

        def setUp(self):
            pass

        def test_one(self):
            self.assertEqual(1, 1)

To use fixture files in a test case they need to be placed in the "fixtures"
directory of an application. Hence the two fixtures in the example correspond
to the following files:

- histograms/fixtures/tests_histograms.json.gz
- inforecords/fixtures/tests_inforecords.json.gz

Existing fixtures content
#########################

The repository contains fixtures that are based on a snapshot of the hisparc
publicdb database on 26 July 2012.

analysissessions/fixtures/tests_analysissessions.json.gz:

- Contains a session based on coincidences for the Science park cluster on 1 May
  2010.

coincidences/fixtures/tests_coincidences.json.gz:

- Includes coincidences for the Science park cluster on 1 May 2010.

histograms/fixtures/tests_histograms.json.gz:

- Summary objects are removed for all but station 501. All objects with a
  reference to those summaries are also removed (DailyDataset, DailyHistogram,
  Configuration and PulseheightFit). Only the summaries of the year
  2011 are kept.
- All PulseheightFit objects are removed except for those between 16 June 2011
  and 9 August 2011.

inforecords/fixtures/tests_inforecords.json.gz:

- Sensitive information has been replaced with placeholders.

Event data
##########

Applications such as "histograms" and "analysissessions" require event data.
Their test suite include functionality to download event data from
data.hisparc.nl. The downloaded files are stored in the path specified by the
variable TEST_DATASTORE_PATH in the file settings.py.


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

    $ cd /srv
    $ mkdir publicdb
    $ chown hisparc.hisparc publicdb
    $ chmod g+rwx publicdb

To set a default ACL entry granting group write permissons for all files,
type::

    $ setfacl -m d:g::rwx publicdb

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
