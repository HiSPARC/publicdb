from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

import datetime

from ..inforecords.models import Station, Cluster, Country, DetectorHisparc
from ..status_display.nagios import status_lists, get_station_status


def station_on_map(request, station_number):
    """Zoom in on a specific station on a map"""

    station_number = int(station_number)
    down, problem, up = status_lists()
    today = datetime.datetime.utcnow()

    center = (DetectorHisparc.objects.filter(station__number=station_number,
                                             startdate__lte=today)
                                     .latest('startdate'))

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in (Station.objects.select_related('cluster__parent',
                                                       'cluster__country')
                                       .filter(cluster=subcluster,
                                               pc__is_active=True,
                                               pc__is_test=False)):
            detector = (DetectorHisparc.objects.filter(station=station,
                                                       startdate__lte=today)
                                               .latest('startdate'))
            status = get_station_status(station.number, down, problem, up)
            stations.append({'number': station.number,
                             'name': station.name,
                             'cluster': station.cluster,
                             'status': status,
                             'longitude': detector.longitude,
                             'latitude': detector.latitude,
                             'altitude': detector.height})
        subclusters.append({'name': subcluster.name,
                            'stations': stations})

    return render_to_response('map.html',
                              {'subclusters': subclusters,
                               'center': center},
                              context_instance=RequestContext(request))


def stations_on_map(request, country=None, cluster=None, subcluster=None):
    """Show all stations from a subcluster on a map"""

    down, problem, up = status_lists()
    today = datetime.datetime.utcnow()

    if country:
        get_object_or_404(Country, name=country)
        if cluster:
            get_object_or_404(Cluster, name=cluster, parent=None,
                              country__name=country)
            if subcluster:
                if cluster == subcluster:
                    get_object_or_404(Cluster, name=subcluster, parent=None)
                else:
                    get_object_or_404(Cluster, name=subcluster,
                                      parent__name=cluster)
                focus = (Cluster.objects.filter(name=subcluster)
                                .values_list('name', flat=True))
            else:
                focus = [Cluster.objects.get(name=cluster, parent=None).name]
                focus.extend(Cluster.objects.filter(parent__name=cluster)
                                    .values_list('name', flat=True))
        else:
            focus = (Cluster.objects.filter(country__name=country)
                            .values_list('name', flat=True))
    else:
        focus = Cluster.objects.all().values_list('name', flat=True)

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in (Station.objects.select_related('cluster__parent',
                                                       'cluster__country')
                                       .filter(cluster=subcluster,
                                               pc__is_test=False)):
            try:
                detector = (DetectorHisparc.objects.filter(station=station,
                                                           startdate__lte=today)
                                                   .latest('startdate'))
            except DetectorHisparc.DoesNotExist:
                continue
            status = get_station_status(station.number, down, problem, up)
            stations.append({'number': station.number,
                             'name': station.name,
                             'cluster': station.cluster,
                             'status': status,
                             'longitude': detector.longitude,
                             'latitude': detector.latitude,
                             'altitude': detector.height})
        subclusters.append({'name': subcluster.name,
                            'stations': stations})

    return render_to_response('map.html',
                              {'subclusters': subclusters,
                               'focus': focus},
                              context_instance=RequestContext(request))
