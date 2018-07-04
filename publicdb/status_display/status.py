import datetime

from ..inforecords.models import Station, Pc
from ..histograms.models import Summary


RECENT_NUM_DAYS = 7


class StationStatus(object):

    """Query the status of a station.

    You can query the status of a single station, or get the status counts for
    all stations.

    """

    def __init__(self):
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        recent_day = datetime.date.today() - datetime.timedelta(days=RECENT_NUM_DAYS)

        self.stations = Station.objects.values_list('number', flat=True)
        self.stations_with_current_data = Summary.objects.filter(date__exact=yesterday).values_list('station__number', flat=True)
        self.stations_with_recent_data = list(Summary.objects.filter(date__gte=recent_day).values_list('station__number', flat=True))
        self.stations_with_pc = Pc.objects.exclude(type__slug='admin').filter(is_active=True).values_list('station__number', flat=True)

    def get_status(self, station_number):
        """Query station status.

        If the station has data as recent as yesterday, it is considered 'up'.
        If it has data in the last RECENT_NUM_DAYS, it is considered 'problem'.
        If it has no recent data, it is considered 'down', unless it has no
        active PC registered, then the status is 'unknown'.

        :param station_number: the station for which to get the statuscount
        :return: 'up', 'problem', or 'down'

        """
        if station_number in self.stations_with_current_data:
            return 'up'
        elif station_number in self.stations_with_recent_data:
            return 'problem'
        elif station_number not in self.stations_with_pc:
            return 'unknown'
        else:
            return 'down'

    def get_status_counts(self):
        """Get the status counts for up, problem and down.

        Count 'up' as all stations with current data. Count 'problem' as all
        stations with recent data except for stations that are 'up'. Count
        'down' as all stations without recent data except for stations that
        have no active PC.

        """

        all_stations = set(self.stations)
        stations_up = set(self.stations_with_current_data)
        stations_recent = set(self.stations_with_recent_data)
        stations_unknown = all_stations.difference(self.stations_with_pc)

        num_up = len(stations_up)
        num_problem = len(stations_recent.difference(stations_up))
        num_down = len(all_stations.difference(stations_recent).difference(stations_unknown))

        return {'up': num_up, 'problem': num_problem, 'down': num_down}
