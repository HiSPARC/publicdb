import os
import sys

dirname = os.path.dirname(__file__)
publicdb_path = os.path.join(dirname, '..')
sys.path.append(publicdb_path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'publicdb.settings'

import django

django.setup()

from publicdb.inforecords.models import *

active_pcs = Pc.objects.filter(is_active=True)
# all_pcs = Pc.objects.all()

contacts = set()
for pc in active_pcs:
    sname = pc.station.name
    sn = str(pc.station.number)
    if pc.station.contact is None:
        continue
    contact_info = pc.station.contact.contactinformation
    email1 = contact_info.email_work.lower() if contact_info.email_work else ''
    email2 = contact_info.email_private.lower() if contact_info.email_private else ''
    contacts.add(email1)
    contacts.add(email2)
    print(';'.join([sname, sn, email1, email2]))

print('\n'.join(contacts))
