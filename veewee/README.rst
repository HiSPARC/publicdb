Building a Vagrant box
======================

We use `Veewee <https://github.com/jedi4ever/veewee>`_ to build our
Vagrant box.


Installing Veewee
-----------------

Veewee is written in Ruby.  On a Mac, you might want to use the Homebrewed
version of Ruby, not the system default::

    $ brew install ruby

On GNU/Linux, Ruby is probably already installed.

The installation instructions included with Veewee encourage you to use
one of several tools to isolate the Veewee gem (a gem is Ruby's equivalent
of a Python package) in a virtualenv.  That did not work for me,
unfortunately.  I gave up and installed Veewee system-wide::

    $ gem install veewee

To verify that the binary is in the correct place and included in your
PATH::

    $ which veewee


Source of the SLC6.4 box definitions
------------------------------------

In a pristine publicdb repository, the veewee directory looks like::

    $ tree
    .
    ├── README.rst
    └── definitions
        └── SLC6.4
            ├── base.sh
            ├── cfengine.sh
            ├── chef.sh
            ├── cleanup.sh
            ├── definition.rb
            ├── ks.cfg
            ├── puppet.sh
            ├── ruby.sh
            ├── vagrant.sh
            ├── virtualbox.sh
            └── zerodisk.sh

The definitions were originally created using (you don't have to run
this!)::

    $ veewee vbox define SLC6.4 'scientificlinux-6.4-x86_64-netboot'

Only slight modifications were made: the number of CPUs was increased to
two.

Furthermore, a default 'hisparc' user was added so that we can simulate an
actual HiSPARC server installation.


Building the Vagrant box
------------------------

Navigate to the veewee directory in the publicdb repository (the directory
containing this very file).  Then issue the following commands::

    $ veewee vbox build --auto SLC6.4
    $ veewee vbox export SLC6.4

The Vagrant box is located in the current working directory.  Building the
box takes approximately 40 minutes.


Updating the Vagrant box
------------------------

You can rebuild the vagrant box by adding the -f option to the build
and export commands.  This will overwrite the previously existing VM.
However, you still need to make sure that vagrant actually uses this new
box.  To achieve this, simply remove the existing vagrant box using::

    $ vagrant destroy
    $ vagrant box remove SLC6.4

You are now in a clean environment and::

    $ vagrant up

will create a new VM using the updated box.
