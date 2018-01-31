#!/usr/bin/env python

import sys
import os
from textwrap import dedent

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'publicdb.settings'

from publicdb.inforecords.models import (Contact, ContactInformation,
                                         Station, Pc)


def prepare_inforecords_fixture():
    for contact in Contact.objects.all():
        contact.first_name = "First_%d" % contact.id
        contact.prefix_surname = ""
        contact.surname = "Sur_%d" % contact.id

        contact.save()

    for contact_info in ContactInformation.objects.all():
        contact_info.street_1 = "Street_%d" % contact_info.id
        contact_info.street_2 = None
        contact_info.postcode = "1000AA"
        contact_info.city = "City_%d" % contact_info.id
        contact_info.pobox = None
        contact_info.pobox_city = None
        contact_info.phone_work = "555-5555"
        contact_info.phone_home = None
        contact_info.fax = None
        contact_info.email_work = "%d@example.com" % contact_info.id
        contact_info.email_private = None
        contact_info.url = None

        contact_info.save()

    for station in Station.objects.all():
        station.password = "Password_%d" % station.id
        station.name = "Name_%d" % station.id
        station.info_page = ""

        station.save()

    for pc in Pc.objects.all():
        pc.name = "Pc_%d" % pc.id
        pc.ip = "127.0.0.%d" % pc.id
        pc.notes = ""

        pc.save()


def print_warning():
    print(dedent("""\
        This script modifies the inforecords tables. It
        replaces sensitive information with placeholder
        values. Since it directly changes the database, you
        have to add the --shut-up argument to imply that you
        know what you are doing.

        Usage: prepare_inforecords_fixture.py --shut-up
    """))


if __name__ == '__main__':
    if len(sys.argv) == 2 and sys.argv[1] == "--shut-up":
        prepare_inforecords_fixture()
    else:
        print_warning()
