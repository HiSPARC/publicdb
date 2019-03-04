# coding: utf-8
import os
import sys

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'publicdb.settings'

import django
django.setup()

from publicdb.inforecords.models import *

active_pcs = Pc.objects.exclude(type__slug='admin').filter(is_active=True)
# all_pcs = Pc.objects.exclude(type__slug='admin').all()


def clean_email(email):
    """ Remove None and make all lowercase"""
    if email is None:
        return ''
    return email.lower()


def extract_email(contact_info):
    email1, email2 = map(clean_email, (contact_info.email_work, contact_info.email_private))
    return email1.lower(), email2.lower()


contacts = set()
for pc in active_pcs:
    sname = pc.station.name
    sn = str(pc.station.number)
    if pc.station.contact is None:
        continue
    email1, email2 = extract_email(pc.station.contact.contactinformation)
    contacts.add(email1)
    contacts.add(email2)

    print ';'.join(item for item in (sname, sn, email1, email2))

print '\n'.join(item for item in contacts)
