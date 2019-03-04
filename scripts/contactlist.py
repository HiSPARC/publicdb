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

contacts = set()
for pc in active_pcs:
    sname = pc.station.name
    sn = str(pc.station.number)
    contact_info = pc.station.contactinformation
    email1 = contact_info.email_work.lower() if contact_info.email_work else ''
    email1 = contact_info.email_private.lower() if contact_info.email_private else ''
    contacts.add(email1)
    contacts.add(email2)
    print(';'.join([sname, sn, email1, email2]))

print('\n'.join(contacts))
