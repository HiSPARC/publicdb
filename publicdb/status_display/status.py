import datetime

from publicdb.histograms.models import Summary


RECENT_NUM_DAYS = 7
RECENT_THRESHOLD = 4


def get_status_func():
    """Return function to query the status of a station.

    The status can be queried by calling function(station_number). If the
    station has data as recent as yesterday, it is considered 'up'. If it has
    at least RECENT_THRESHOLD days of data in the last RECENT_NUM_DAYS, it is
    considered 'problem'. If it has less data than the threshold, it is
    considered 'down'.

    """
    yesterday = datetime.date.today() - datetime.timedelta(days=1)
    recent_day = datetime.date.today() - datetime.timedelta(days=RECENT_NUM_DAYS)

    stations_with_current_data = [x.station.number for x in Summary.objects.filter(date__exact=yesterday)]
    stations_with_recent_data = [x.station.number for x in Summary.objects.filter(date__gte=recent_day)]

    def get_status(station_number):
        if station_number in stations_with_current_data:
            return 'up'
        elif stations_with_recent_data.count(station_number) > RECENT_THRESHOLD:
            return 'problem'
        else:
            return 'down'

    return get_status
