import sys
import os
import csv

sys.path.append('../')
os.environ['DJANGO_SETTINGS_MODULE'] = 'controlpanel.settings'

from controlpanel.inforecords.models import Cluster, Location, Station

if __name__ == '__main__':
    writer = csv.writer(sys.stdout)

    for cluster in Cluster.objects.all().order_by('id'):
        for station in Station.objects.filter(location__cluster=cluster):
            writer.writerow((station.number, cluster.id, station.password,
                             station.location.name))
