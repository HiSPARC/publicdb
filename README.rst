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

    ===================================================================
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

    $ pip install ipython==0.13.1

    $ pip install Cython==0.17.1
    $ pip install numpy==1.6.2

    $ pip install numexpr==2.0.1
    $ pip install tables==2.4.0

    $ pip install recaptcha-client==1.0.6

    $ pip install Django==1.4.3
    $ pip install South==0.7.3

You now have all the prerequisites for running the publicdb django app.
For reference, the results from `pip freeze`::

    $ pip freeze
    Cython==0.16
    Django==1.4.2
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

You can also use vagrant to set up a personal development environment in a virtualbox
-------------------------------------------------------------------------------------

Centos will be downloaded on the virtualbox. On this box all the required
programms, will be downloaded. Also their will be a shared folder created.
This folder is called vagrant in the box and it contains the folder publicdb.

First, `Vagrant <http://vagrantup.com/>`_ has to be installed.

Second, open a terminal. Go to the place where the Vagrantfile is located,
this file is located at [PATHO]/publicdb/vagrant/. 

To run vagrant and download the needed programms,  
do ::
    $ vagrant up

To start the box after everything is downloaded,
do ::
    $ vagrant ssh

To activate the virtual environment in the box,
do ::
    $ source /srv/publicdb/publicdb_env/bin/activate
    
After that you need to start supervisor with ::
    $ sudo /sbin/service supervisord start
    
At last, to start the testserver ::
    $ cd /srv/publicdb/www
    $ sudo uwsgi --ini uwsgi.ini
    
Every file that is beeing changed in [PATHO]/publicdb, will automaticcaly be 
changed in the virtalbox. This is the same, for everything that you change
in the virtualbox. 


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
