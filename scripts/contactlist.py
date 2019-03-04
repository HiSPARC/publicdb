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


def clean_email(email):
    """ Remove None and make all lowercase"""
    if email is None:
        return ''
    return email.lower()


contacts = set()
for pc in active_pcs:
    sname = pc.station.name
    sn = str(pc.station.number)
    contact_info = pc.station.contactinformation
    email1, email2 = map(clean_email, (contact_info.email_work, contact_info.email_private))

    email1 = email1.lower()
    email2 = email2.lower()
    contacts.add(email1)
    contacts.add(email2)
    print ';'.join(item for item in (sname, sn, email1, email2))

print '\n'.join(item for item in contacts)
