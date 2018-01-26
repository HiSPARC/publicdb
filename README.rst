HiSPARC Public Database README
==============================


.. image:: http://img.shields.io/badge/license-GPLv3-blue.svg
   :target: https://github.com/HiSPARC/publicdb/blob/master/LICENSE
.. image:: http://img.shields.io/travis/HiSPARC/publicdb/master.svg
   :target: https://travis-ci.org/HiSPARC/publicdb
.. image:: http://img.shields.io/coveralls/github/HiSPARC/publicdb/master.svg?label=coveralls
   :target: https://coveralls.io/github/HiSPARC/publicdb
.. image:: http://img.shields.io/codecov/c/github/HiSPARC/publicdb/master.svg?label=codecov
   :target: https://codecov.io/github/HiSPARC/publicdb


Overview
--------

The HiSPARC Public Database is a Django application which stores derived
data and displays it for public use.  It exposes an API to download raw
detector data from the datastore, as well as an API to participate in
analysis sessions.

To run and test the code, you can either set up a personal development
environment containing all necessary libraries, or you can use Vagrant and
Virtualbox to run everything in a virtual machine.


.. contents:: Table of Contents
   :backlinks: none


Using Vagrant to run inside a virtual machine
---------------------------------------------

We use `Vagrant <http://www.vagrantup.com>`_ to set up a virtual machine
nearly identical to our production server *Pique*.  The VM runs on
Virtualbox.  We use multiple VMs for different tasks.  We'll focus on the ``publicdb`` VM.

You can download Vagrant and Virtualbox binaries for all
major platforms.  On a Mac::

   $ brew cask install virtualbox
   $ brew cask install vagrant

Kernel upgrades in the VM can break the Virtualbox guest modules, which
need to be rebuilt.  There is a nice plugin for vagrant which checks if
the module version matches the virtualbox version and if the modules are
loaded or need to be rebuilt.  This also handles upgrading Virtualbox
itself.  Install the plugin with::

   $ vagrant plugin install vagrant-vbguest

To correctly provision the VM, you need to have Python installed, with the
`Ansible <http://www.ansibleworks.com>`_ package, available from PyPI.
Shortcut on a Mac::

    $ brew install ansible

Then, navigate to the publicdb repository root and::

    $ vagrant up publicdb

You can ssh into you box by issuing::

    $ vagrant ssh publicdb

To halt the VM, issue::

    $ vagrant halt publicdb

Please consult the `Vagrant documentation
<https://www.vagrantup.com/docs/>`_ for further instructions on using
Vagrant.


Creating the Vagrant base box
-----------------------------

The Vagrant base box is created using `Packer <https://www.packer.io>`_.
We formerly used Veewee, but Packer sees more active development and
allows us to pre-provision the base box.  If you want to build your own
base box, you can install Packer on a Mac using::

    $ brew install packer

Then, navigate to the packer/CentOS6/ directory and issue::

    $ packer build template.json

If you need to really make sure the new box is used, remove the old box
from Vagrant::

    $ vagrant box remove CentOS6

And you can simply::

    $ vagrant up [machine]


Hints for running a development publicdb server
-----------------------------------------------

In order to create a tiny copy of the datastore for development purposes,
do::

    $ python scripts/download_test_datastore.py

To generate the histograms for the downloaded data::

    $ python scripts/hisparc-update.py

If you have access to a `publicdb_dump.sql` file to fill the database with,
place the file in the publicdb directory, log into the machine, and load the
file into the database, this can be done using the following commands::

    $ mv [path/to/publicdb.sql] ./
    $ vagrant ssh publicdb
    $ pg_restore --clean --if-exists --no-owner --no-acl --schema=public --dbname=publicdb /vagrant/publicdb_dump.sql


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

The *only* way to get into the machine is via SSH, so *don't lock yourself out!* (Actually, there is another way. With console access, you can reboot in single user mode.)


Provisioning production servers
-------------------------------

We use Ansible for all our provisioning needs. You can run it from the top repository
directory. At that location, there is a file called ``ansible.cfg`` which sets up a few
config values. To run the playbook, issue::

   $ ansible-playbook provisioning/playbook.yml

Beware, however, that this will run provisioning for *all* production *and* virtual servers. It is *very* useful to limit the hosts for which to run the provisioner, e.g.::

   $ ansible-playbook provisioning/playbook.yml -l tietar.nikhef.nl

If you want to check first what the provisioner would like to change, without actually changing anything, use the ``-C`` option::

   $ ansible-playbook provisioning/playbook.yml -l tietar.nikhef.nl -C


Running a provisioner from a remote location
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To manage the servers from somewhere out on the internet, you have to work with an SSH
tunnel. Basically, you SSH into ``login.nikhef.nl`` and route all traffic destined for the
production servers through that connection. So you never log into Tietar or Pique from
your remote location. Instead, from your location, you log into ``login.nikhef.nl``, and
from there, you log into Tietar or Pique. To make that work more or less transparently,
we'll have to setup a few things. Every tunnel needs a port number, and I (DF) have chosen
a few completely arbitrary ones:

==========  ===========  ===========
Local port  Remote host  Remote port
==========  ===========  ===========
2201        pique        22
2202        tietar       22
2203        frome        22
==========  ===========  ===========

If you're using some unix-style OS, like Linux, OS X or macOS, you can use the provided setup-tunnel.sh like so::

   $ sh provisioning/setup-tunnel.sh <nikhef_username>

For example::

   $ sh provisioning/setup-tunnel.sh davidf

You can also use an application like *SSH Tunnel Manager* by Tynsoe or *SSH Tunnel* by Codinn.

If you're on Windows or something, you can look into PuTTY and setup the tunnels that way.

Once you have everything up and running, you have to use a different Ansible inventory
file. That is needed to tell Ansible to use the tunnels, and not a direct connection. One
is provided, so you can run::

   $ ansible-playbook provisioning/playbook.yml -i provisioning/ansible_inventory_tunnel -l tietar.nikhef.nl

If you want to provision all servers at once, you can leave off the ``-l`` option.

Provisioning using a Windows host
---------------------------------

Ansible does not support windows as a host (control machine). On Windows
the ``ansible_local`` provisioner is used.

All scripts that are passed to ``/bin/bash`` on the target CentOS6 machine
will fail miserably when carriage returns (CR, ^M, 0x0D) are present. This
will cause all sorts of strange, hard to track down, errors. Make sure all
files have unix-like line-endings (LF not CRLF)::

   $ git config --global core.autocrlf "input"
   $ git clone git@github.com:HiSPARC/publicdb.git

Check ``packer/CentOS6/http/ks.cfg`` and ``provisioning/*sh`` for carriage
returns.

Build the base box using packer.

Now add the VM::

   $ vagrant up publicdb

Provisioning might stop if the kernel of the guest VM is upgraded, because
this will trigger a reboot. Reload and restart provisioning::

   $ vagrant reload publicdb --provision
