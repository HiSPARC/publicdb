import datetime

from publicdb.inforecords.models import Station, Pc
from publicdb.histograms.models import Summary


RECENT_NUM_DAYS = 7
RECENT_THRESHOLD = 4


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
        If it has at least RECENT_THRESHOLD days of data in the last
        RECENT_NUM_DAYS, it is considered 'problem'. If it has less data than
        the threshold, it is considered 'down'.

        :param station_number: the station for which to get the statuscount
        :return: 'up', 'problem', or 'down'

        """
        if station_number in self.stations_with_current_data:
            return 'up'
        elif self.stations_with_recent_data.count(station_number) >= RECENT_THRESHOLD:
            return 'problem'
        elif station_number not in self.stations_with_pc:
            return 'unknown'
        else:
            return 'down'

    def get_status_counts(self):
        """Get the status counts for up, problem and down."""

        num_up = [u in self.stations_with_current_data for u in self.stations].count(True)
        num_problem = [self.stations_with_recent_data.count(u) >= RECENT_THRESHOLD for u in self.stations].count(True)
        num_down = [self.stations_with_recent_data.count(u) < RECENT_THRESHOLD for u in self.stations].count(True)

        return {'up': num_up, 'problem': num_problem, 'down': num_down}
