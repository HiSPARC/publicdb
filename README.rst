HiSPARC Public Database README
==============================


.. image:: http://img.shields.io/badge/license-GPLv3-blue.svg
   :target: https://github.com/HiSPARC/publicdb/blob/master/LICENSE
.. image:: http://img.shields.io/github/status-checks/HiSPARC/publicdb/master.svg
   :target: https://github.com/HiSPARC/publicdb/actions


Overview
--------

The HiSPARC Public Database is a Django application which stores derived
data and displays it for public use.  It exposes an API to download raw
detector data from the datastore, as well as an API to participate in
analysis sessions.

To run and test the code, you can use Docker to setup a contained test
environment.

.. contents:: Table of Contents
   :backlinks: none


Important information regarding provisioning the production servers
-------------------------------------------------------------------

When you first run ansible on a freshly-installed system, you're likely to run into an error like::

   sudo: sorry, you must have a tty to run sudo

You can fix that by manually logging into the machine, and typing::

   $ sudo visudo

And changing the line::

   Defaults requiretty

to::

   Defaults !requiretty

Also, lock the root account and the user account. First, make sure to add your public key
to ``~/.ssh/authorized_keys``, with the mode of both the directory and the file set to
``0600``. First make sure to test logging in without a password!!! Only then, lock the
accounts::

   $ sudo passwd -l root
   $ sudo passwd -l hisparc

The *only* way to get into the machine is via SSH, so *don't lock yourself out!* (Actually,
there is another way. With console access, you can reboot in single user mode.)


Provisioning production servers
-------------------------------

We use Ansible for all our provisioning needs. You can run it from the top repository
directory. At that location, there is a file called ``ansible.cfg`` which sets up a few
config values. To run the playbook, issue::

   $ ansible-playbook provisioning/playbook.yml

Beware, however, that this will run provisioning for *all* production servers.
It is *very* useful to limit the hosts for which to run the provisioner, e.g.::

   $ ansible-playbook provisioning/playbook.yml -l publicdb

If you want to check first what the provisioner would like to change, without actually changing anything, use the ``-C`` option::

   $ ansible-playbook provisioning/playbook.yml -l publicdb -C


Running a provisioner from a remote location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The servers can not be accessed directly from outside the university network.
However, if there is a jump server available, it can easily be configured to
automatically be used by setting it in your ssh configuration.

Add this to your ``.ssh/config``::

    Host hisparc-data hisparc-raw
        ProxyJump notchpeak1.chpc.utah.edu


Running with Docker-compose
---------------------------

Install and start Docker, then in this directory do::

    $ docker-compose up -d

If this is the first run you should now run database migrations::

    $ docker-compose exec publicdb ./manage.py migrate

In order to populate the database you can use a dump of the production
database::

    $ docker-compose exec -T postgres pg_restore --username=hisparc --dbname=publicdb < publicdb_dump.sql

or create some fake data::

    $ docker-compose exec publicdb ./manage.py createfakedata

To clean the database again to fill it with new fake data use::

    $ docker-compose exec publicdb ./manage.py flush --noinput
    $ docker-compose exec publicdb ./manage.py loaddata publicdb/histograms/fixtures/initial_generator_state.json
    $ docker-compose exec publicdb ./manage.py loaddata publicdb/histograms/fixtures/initial_types.json


Hints for running a development publicdb server
-----------------------------------------------

In order to create a tiny copy of the datastore for development purposes,
do::

    $ python scripts/download_test_datastore.py

To generate the histograms for the downloaded data::

    $ ./manage.py updatehistograms
