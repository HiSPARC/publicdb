from django.http import Http404
from django.shortcuts import get_object_or_404, render

from ..inforecords.models import Cluster, Country, Station
from ..status_display.status import DataStatus
from ..status_display.views import stations_with_data


def station_on_map(request, station_number):
    """Zoom in on a specific station on a map"""

    station = get_object_or_404(Station, number=station_number)
    center = station.latest_location()
    if center['latitude'] is None and center['longitude'] is None:
        raise Http404

    subclusters = get_subclusters()

    return render(request, 'maps/map.html', {'subclusters': subclusters, 'center': center})


def get_focus(country=None, cluster=None, subcluster=None):
    if not country:
        return Cluster.objects.all().values_list('name', flat=True)

    country = get_object_or_404(Country, name=country)

    if not cluster:
        return country.clusters.values_list('name', flat=True)

    cluster = get_object_or_404(country.clusters, name=cluster, parent=None)

    if not subcluster:
        focus = [cluster.name]
        focus.extend(cluster.subclusters.values_list('name', flat=True))
        return focus

    if cluster.name == subcluster:
        return [cluster.name]

    subcluster = get_object_or_404(cluster.subclusters, name=subcluster)

    return [subcluster.name]


def stations_on_map(request, country=None, cluster=None, subcluster=None):
    """Show all stations from a subcluster on a map"""

    focus = get_focus(country, cluster, subcluster)
    subclusters = get_subclusters()

    return render(request, 'maps/map.html', {'subclusters': subclusters, 'focus': focus})


def get_subclusters():
    data_stations = stations_with_data()
    station_status = DataStatus()

    subclusters = []
    for subcluster in Cluster.objects.all():
        stations = []
        for station in subcluster.stations.filter(pcs__is_test=False).distinct():
            link = station in data_stations
            status = station_status.get_status(station.number)
            location = station.latest_location()
            station_data = {
                'number': station.number,
                'name': station.name,
                'cluster': subcluster,
                'link': link,
                'status': status,
            }
            station_data.update(location)
            stations.append(station_data)
        subclusters.append({'name': subcluster.name, 'stations': stations})
    return subclusters
