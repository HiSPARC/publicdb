Building a Vagrant box
======================

We use `Veewee <https://github.com/jedi4ever/veewee>`_ to build our
Vagrant box.


Installing Veewee
-----------------

The installation instructions included with Veewee encourage you to use
one of several tools to isolate the Veewee gem (a gem is Ruby's equivalent
of a Python package) in a virtualenv.  That did not work for me,
unfortunately.  I gave up and installed Veewee system-wide.  This option
is not included in the documentation.  You are encouraged by the Veewee
team to build Veewee from source.  On a Mac, you might want to use the
Homebrewed version of Ruby, not the system default::

    $ brew install ruby

To clone the Veewee repository::

    $ git clone https://github.com/jedi4ever/veewee.git

To build the gem::

    $ cd veewee/
    $ gem build veewee.gemspec
    $ gem install veewee-0.3.7.gem

To verify that the binary is in the correct place and included in your
PATH::

    $ cd
    $ which veewee


Source of the SLC5.9 box definitions
------------------------------------

In a pristine publicdb repository, the veewee directory looks like::

    $ tree
    .
    └── definitions
        └── SLC5.9
            ├── definition.rb
            ├── ks.cfg
            └── postinstall.sh

The definitions were originally created using::

    $ veewee vbox define SLC5.9 'scientificlinux-5.9-x86_64'

Only slight modifications were made: the number of CPUs was increased to
two, the amount of memory was increased to 512 Mb and the kernel parameter
'divider=10' was added to work around an issue of the VM using a lot of
CPU because of a high-frequency clock interrupt.

Furthermore, a default 'hisparc' user was added so that we can simulate an
actual HiSPARC server installation.


Building the Vagrant box
------------------------

Navigate to the veewee directory in the publicdb repository (the directory
containing this very file).  Then issue the following commands::

    $ veewee vbox build --auto SLC5.9
    $ veewee vbox export SLC5.9

The Vagrant box is located in the current working directory.


Updating the Vagrant box
------------------------

You can rebuild the vagrant box by adding the -f option to the build
and export commands.  This will overwrite the previously existing VM.
However, you still need to make sure that vagrant actually uses this new
box.  To achieve this, simply remove the existing vagrant box using::

    $ vagrant destroy
    $ vagrant box remove SLC5.9

You are now in a clean environment and::

    $ vagrant up

will create a new VM using the updated box.
