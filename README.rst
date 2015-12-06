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
Virtualbox.  You can download Vagrant and Virtualbox binaries for all
major platforms.  On a Mac::

   $ brew install caskroom/cask/brew-cask
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

    $ vagrant up

You can ssh into you box by issuing::

    $ vagrant ssh

To halt the VM, issue::

    $ vagrant halt

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

Then, navigate to the packer/CentOS6.6/ directory and issue::

    $ packer build template.json

If you need to really make sure the new box is used, remove the old box
from Vagrant::

    $ vagrant box remove CentOS6.6

And you can simply `vagrant up`.


Hints for running a development publicdb server
-----------------------------------------------

In order to create a tiny copy of the datastore for development purposes,
do::

    $ python scripts/download_test_datastore.py

To generate the histograms for the downloaded data::

    $ python scripts/hisparc-update.py


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

however, this also include the tests defined in the Django framework itself and
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
