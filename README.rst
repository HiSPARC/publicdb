HiSPARC Public Database README
==============================


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
<http://docs.vagrantup.com/v2/>`_ for further instructions on using
Vagrant.


Creating the Vagrant base box
-----------------------------

The Vagrant base box is created using `Packer <https://www.packer.io>`_.
We formerly used Veewee, but Packer sees more active development and
allows us to pre-provision the base box.  If you want to build your own
base box, you can install Packer on a Mac using::

    $ brew cask install packer

Then, navigate to the packer/CentOS6/ directory and issue::

    $ packer build template.json

If you need to really make sure the new box is used, remove the old box
from Vagrant::

    $ vagrant box remove CentOS6

And you can simply `vagrant up`.


Hints for running a development publicdb server
-----------------------------------------------

In order to create a tiny copy of the datastore for development purposes,
do::

    $ python scripts/download_test_datastore.py

To generate the histograms for the downloaded data::

    $ python scripts/hisparc-update.py


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

Also, lock the root account and the user account. First, make sure to add your public key to ``~/.ssh/authorized_keys``, with the mode of both the directory and the file set to ``0600``. First make sure to test logging in without a password!!! Only then, lock the accounts::

   $ sudo passwd -l root
   $ sudo passwd -l hisparc
