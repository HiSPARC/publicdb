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

Besides all the Python packages that will need to be installed next
you also need the HDF5 libraries.  These are required to work with
the h5 data files and to install the python tables package.  So download
the source::

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

    $ mkvirtualenv publicdb

where you can replace *publicdb* with any name you like.  If the
environment is not already automatically activated, do that with::

    $ workon publicdb

We will now populate this environment with all prerequisites.  To
duplicate the environment used while writing this documentation, use the
following instructions, including version numbers.  To install the latest
versions of the software, drop the `==<version>` part.  For example, you
can install ipython 0.13.1 using::

    $ pip install ipython==0.13.1

Alternatively, install the latest version with::

    $ pip install ipython

The complete requirements and installation instructions are::

    $ pip install ipython==0.13.2

    $ pip install numpy==1.7.1

    $ pip install Cython==0.19
    $ pip install numexpr==2.1
    $ pip install tables==2.4.0

    $ pip install recaptcha-client==1.0.6

    $ pip install Django==1.4.3
    $ pip install South==0.7.6
    $ pip install docutils==0.10

    $ pip install progressbar==2.3
    $ pip install mock==1.0.1
    $ pip install scipy==0.12.0
    $ pip install matplotlib==1.2.1
    $ pip install https://github.com/hisparc/sapphire/zipball/master

You now have all the prerequisites for running the publicdb django app.
For reference, the results from `pip freeze`::

    $ pip freeze
    Cython==0.19
    Django==1.4.3
    South==0.7.6
    docutils==0.10
    ipython==0.13.2
    matplotlib==1.2.1
    mock==1.0.1
    numexpr==2.1
    numpy==1.7.1
    progressbar==2.3
    recaptcha-client==1.0.6
    sapphire==0.9.1b
    scipy==0.12.0
    tables==2.4.0
    wsgiref==0.1.2

Note for Mac OS X users: python has trouble detecting the default locale.
Before continuing, it's best to type this into your terminal::

    $ export LC_ALL=en_US.UTF-8

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

Run the django-cron.py in the examples folder to generate the histograms
for the downloaded data::

    $ python django-cron.py

You can start the Django development server from inside the Django app
directory (the one containing your settings.py) with::

    $ ./manage.py runserver


Deployment
----------

Initial draft.

Op Pique::

    /srv bestaat al.

    # cd /srv
    # mkdir publicdb
    # chown hisparc.hisparc publicdb
    # chmod g+rwx publicdb
    # setfacl -m d:g::rwx publicdb

    ---> als user davidf?

    $ cd publicdb
    $ git clone https://github.com/HiSPARC/publicdb.git www
    $ chmod g+w www
    $ mkdir static
    $ virtualenv --distribute publicdb_env

    $ source /srv/publicdb/publicdb_env/bin/activate
    (publicdb env install instructies gevolgd)

    $ pip install uwsgi uwsgitop
    $ pip install mysql-python
