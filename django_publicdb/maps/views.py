from django.shortcuts import render, get_object_or_404
from django.http import Http404

from ..inforecords.models import Station, Cluster, Country
from ..status_display.nagios import status_lists, get_station_status


def station_on_map(request, station_number):
    """Zoom in on a specific station on a map"""

    station_number = int(station_number)
    down, problem, up = status_lists()

    station = get_object_or_404(Station, number=station_number)
    center = station.latest_location()
    if center['latitude'] is None and center['longitude'] is None:
        raise Http404

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in (Station.objects.select_related('cluster__parent',
                                                       'cluster__country')
                                       .filter(cluster=subcluster,
                                               pc__is_active=True,
                                               pc__is_test=False)):
            location = station.latest_location()
            status = get_station_status(station.number, down, problem, up)
            station_data = {'number': station.number,
                            'name': station.name,
                            'cluster': station.cluster,
                            'status': status}
            station_data.update(location)
            stations.append(station_data)
        subclusters.append({'name': subcluster.name,
                            'stations': stations})

    return render(request, 'map.html',
                  {'subclusters': subclusters,
                   'center': center})


def stations_on_map(request, country=None, cluster=None, subcluster=None):
    """Show all stations from a subcluster on a map"""

    down, problem, up = status_lists()

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
            location = station.latest_location()
            status = get_station_status(station.number, down, problem, up)
            station_data = {'number': station.number,
                            'name': station.name,
                            'cluster': station.cluster,
                            'status': status}
            station_data.update(location)
            stations.append(station_data)
        subclusters.append({'name': subcluster.name,
                            'stations': stations})

    return render(request, 'map.html',
                  {'subclusters': subclusters,
                   'focus': focus})
