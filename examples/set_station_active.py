import sys
import os
import MySQLdb
import datetime

sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'controlpanel.settings'

import controlpanel.inforecords.models as inforecords

if __name__ == '__main__':
    db = MySQLdb.connect('127.0.0.1', 'analysis', 'Data4analysis!',
                         'eventwarehouse', 3307)
    cursor = db.cursor()

    since = datetime.date.today() - datetime.timedelta(weeks=4)

    for pc in inforecords.Pc.objects.exclude(
                    type__description='Admin PC'):

        sql = ("SELECT event_id FROM event WHERE eventtype_id=1 AND "
               "station_id=%s AND date > %s LIMIT 1")

        cursor.execute(sql, (pc.station.number, since))
        if cursor.fetchone():
            print ('Setting pc %s from station %d active' % 
                (pc, pc.station.number))
            pc.is_active = True
            pc.save()

    cursor.close()
    db.close()
