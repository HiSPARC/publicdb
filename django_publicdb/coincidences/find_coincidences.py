from MySQLdb import connect
from math import sqrt, sin, cos, pi
import zlib
from django_publicdb.inforecords.models import DetectorHisparc, Station

COINCIDENCE_WINDOW = 2e5    # in nanoseconds
ADCOFFSET = 114.
ADCGAIN = -0.57


def get_db_cursor():
    """
    Connect to the eventwarehouse
    """
    DB_HOST = 'peene'
    DB_USER = 'analysis'
    DB_PASSW = 'Data4analysis!'
    DB_NAME = 'eventwarehouse'

    conn = connect(DB_HOST, DB_USER, DB_PASSW, DB_NAME)
    cursor = conn.cursor()
    return cursor

    
def get_events(day, station, t1, t2):
    """
    Get the timestamps for the events occurred on date 'day'
    in detector 'station'
    
    return: dict(event_id : {details,})
    """
    cursor = get_db_cursor()
    query = "SELECT e.event_id, e.time, e.nanoseconds " \
            "FROM event e " \
            "WHERE e.station_id = %d AND e.eventtype_id = 1 " \
            "AND e.date = '%s' AND e.time >= '%s' AND e.time <= '%s' " \
            % (station, day, t1, t2)
    cursor.execute(query)
    
    events = {}
    for eventID, t, n in cursor.fetchall():
        t_spl = str(t).split(':')
        timestamp = int(t_spl[0])*3.6e12 + int(t_spl[1])*6e10 + int(t_spl[2])*1e9 + n
        
        if not int(eventID) in events:
            events[int(eventID)] = dict([('date',day), ('time',t), ('nanoseconds',n), \
                                        ('timestamp',timestamp), ('detector',int(station)), \
                                        ('latitude',0), ('longitude',0), ('height',0), \
                                        ('PH1',0), ('PH2',0), ('PH3',0), ('PH4',0), \
                                        ('IN1',0), ('IN2',0), ('IN3',0), ('IN4',0), \
                                        ('TR1',0), ('TR2',0), ('TR3',0), ('TR4',0)])
            
            (events[int(eventID)])['latitude'] = \
                (DetectorHisparc.objects.get( station__number = int(station) ) ).latitude
            (events[int(eventID)])['longitude'] = \
                (DetectorHisparc.objects.get( station__number = int(station) ) ).longitude
            (events[int(eventID)])['height'] = \
                (DetectorHisparc.objects.get( station__number = int(station) ) ).height

            #if int(station) == 501: #NIKHEF
                #(events[int(eventID)])['latitude'] = 52.355905
                #(events[int(eventID)])['longitude'] = 4.951221
            #elif int(station) == 502: #Anton Pannekoek
                #(events[int(eventID)])['latitude'] = 52.355294
                #(events[int(eventID)])['longitude'] = 4.950215
            #elif int(station) == 503: #SARA
                #(events[int(eventID)])['latitude'] = 52.35619
                #(events[int(eventID)])['longitude'] = 4.952814
                #(events[int(eventID)])['timestamp'] -= 15
            #elif int(station) == 504: #MATRIX
                #(events[int(eventID)])['latitude'] = 52.357024
                #(events[int(eventID)])['longitude'] = 4.95445
            #elif int(station) == 505: #PIMU
                #(events[int(eventID)])['latitude'] = 52.357223
                #(events[int(eventID)])['longitude'] = 4.94841
     
    return events


def search_coincidences(detectors, day, start, end):
    """
    search for coincidences in the data from the
    detectors in the list
    """
    
    # put the timestamps of the detectors in a dictionary
    event_dict = {}    # the events of all the detectors combined
    double_ts = {}
    timestamps = []
    ts_dict = {}
    for det in detectors:
        events = get_events(day, det, start, end)
        for eventID,details in events.iteritems():
            while(details['timestamp'] in timestamps):   # we cannot have double timestamps
                details['timestamp'] += 1   # we set it back later
                if eventID in double_ts:
                    double_ts[eventID] += 1
                else:
                    double_ts[eventID] = 1
            
            event_dict[eventID] = details
            timestamps.append(details['timestamp'])
            ts_dict[details['timestamp']] = eventID
            
    timestamps.sort()
    
    # iterate through the list with all timestamps to find coincidences
    # in the COINCIDENCE_WINDOW
    coincidences = [(0,),]
    for ts_ref in timestamps:
        for ts in timestamps[(timestamps.index(ts_ref) +1):]:
            if (ts - ts_ref) < COINCIDENCE_WINDOW:      # coincidence found
                if ts_ref == (coincidences[-1])[0]:
                    coincidences[-1].append( ts )
                else:
                    coincidences.append([ts_ref,ts])
            else:
                break
    coincidences.remove((0,))
   
    # convert the coincidence list of timestamps to
    # a list of event ids
    coincidences_ids = []
    for coincidence in coincidences:
        c_ids = []
        for timestamp in coincidence:
            c_ids.append(ts_dict[timestamp])
        coincidences_ids.append(c_ids)
    coincidences = coincidences_ids
    
    # set the timestamps which were double back to their
    # original value
    for eventID in double_ts:
        (event_dict[eventID])['timestamp'] -= double_ts[eventID]
    
    # remove coincidinces with only two events
    coincidences = filter_duos(coincidences)
    
    # check if a coincidence is a subset of a previous coincidence
    coincidences = filter_subsets(coincidences)
 
    # check if a coincidence has a detector more than once
    coincidences = filter_double_detectors(coincidences, event_dict)
    
    # check the coincidence with a detector-specific coincidence window
    coincidences = filter_timediff_distance(coincidences, event_dict)
    
    # add the traces of the events that have a coincidence
    add_event_data(event_dict, coincidences)

    #print ']\n'.join( str(coincidences).split('], ') )
    #print event_dict[(coincidences[0])[0]]

    return event_dict, coincidences


def filter_duos(coincidences):
    """
    Remove the coincidences with only
    two events
    """
    to_be_removed = []
    for coincidence in coincidences:
        if len(coincidence) == 2:
            to_be_removed.append(coincidence)
    
    for coincidence in to_be_removed:
        coincidences.remove(coincidence)

    
    return coincidences
    

def filter_subsets(coincidences):
    """
    Check if the set of coincidences
    cointain a coincidence which is a subset
    of another coincidence
    require: the list of coincidences is ordered
    """
    to_be_removed = []
    rem = False
    prev = []
    for coincidence in coincidences:
        if len(coincidence) == (len(prev) -1):
            for i in range(len(coincidence)):
                if coincidence[i] == prev[i+1]:
                    rem = True
                else:
                    rem = False
            if rem:
                to_be_removed.append(coincidence)
                rem = False
        prev = coincidence
    
    for coincidence in to_be_removed:
        coincidences.remove(coincidence)
    
    return coincidences

    
def filter_double_detectors(coincidences, event_dict):
    """
    Check if the coincidences have one or more
    detectors more than once
    If so, flag it with "DOUBLE"
    """
    for coincidence in coincidences:
        det_in_c = []   # detectors in a coincidence
        for eventID in coincidence:
            if type(eventID) == type('string'):   # coincidence is already flagged
                break
            det_in_c.append( (event_dict[eventID])['detector'] )
        
        # if the coincidence has doubles, flag it
        if len( det_in_c ) != len( dict.fromkeys(det_in_c).keys() ):
            coincidence.append("DOUBLE")

    return coincidences


def filter_timediff_distance(coincidences, event_dict):
    """
    Filter the coincidences with detector specific
    coincidence window
    If time difference is too big, flag it with "TOOLATE"
    """
    c = 299792458
    toolate = False
    for coincidence in coincidences:
        details = event_dict[coincidence[0]]
        first_detector = [details['timestamp'],]
        first_detector.extend( WGS84_xyz(details['latitude'], details['longitude'], details['height']) )
        for eventID in coincidence[1:]:
            if type(eventID) != type('string'):
                details = event_dict[eventID]
                detector = [details['timestamp'],]
                detector.extend( WGS84_xyz(details['latitude'], details['longitude'], details['height']) )
            
                timediff = (detector[0] - first_detector[0]) / 1e9
                distance = sqrt( (first_detector[1] - detector[1])**2 + \
                             (first_detector[2] - detector[2])**2 + \
                             (first_detector[3] - detector[3])**2 )
                
                if distance < (timediff*c):
                    toolate = True
                    break
        if toolate:
            coincidence.append('TOOLATE')
            toolate = False
            
    return coincidences


def WGS84_xyz(lat, lon, h):
    """
    convert the lat long h from WGS84 to cartesian coordinates
    """
    lat = lat * (pi/180)
    lon = lon * (pi/180)
    
    a = 6378137.0           # major semi-axis of reference ellipsoid
    b = 6356752.3142        # minor semi-axis of reference ellipsoid
    
    ecc_sq = 0.00669437999014   # first eccentricity squared of the reference ellipsoid
    N = a / sqrt( 1 - (ecc_sq * sin(lat)**2) ) # prime vertical radius of curvature
    
    X = (N+h) * cos(lat) * cos(lon)
    Y = (N+h) * cos(lat) * sin(lon)
    Z = ((N*(1-ecc_sq))+h) * sin(lat)
    
    return [X,Y,Z]


def add_event_data(event_dict, coincidences):
    """
    Add the data (like traces, location) to the events that have are part of a coincidence
    """
    cursor = get_db_cursor()

    for coincidence in coincidences:
        for eventID in coincidence:
            if type(eventID) == type(123):
                query = "SELECT edt.uploadcode, ed.blobvalue , cdt.uploadcode, cd.doublevalue " \
                        "FROM event e " \
                        "JOIN eventdata ed USING (event_id) " \
                        "JOIN eventdatatype edt USING (eventdatatype_id) " \
                        "JOIN calculateddata cd USING (event_id) " \
                        "JOIN calculateddatatype cdt USING (calculateddatatype_id) " \
                        "WHERE e.station_id = %d AND e.eventtype_id = 1 " \
                        "AND e.date = '%s' AND e.time = '%s' AND e.nanoseconds = '%s' " \
                        "AND e.event_id = %d " \
                        "AND edt.uploadcode IN ('TR1', 'TR2', 'TR3', 'TR4') " \
                        "AND cdt.uploadcode IN ('PH1', 'PH2', 'PH3', 'PH4','IN1', 'IN2', 'IN3', 'IN4')" \
                        % ( (event_dict[eventID])['detector'], (event_dict[eventID])['date'], \
                            (event_dict[eventID])['time'], (event_dict[eventID])['nanoseconds'], \
                            eventID )
                cursor.execute(query)

                for edt_code, ed_blob, cdt_code, cd_double in cursor.fetchall():
                    if edt_code[:2] == 'TR':
                        trace = zlib.decompress( ed_blob )
                        trace = trace.split(',')
                        del(trace[-1])
                        trace = map(lambda x: ((int(x)*ADCGAIN) + ADCOFFSET), trace)
                        (event_dict[eventID])[edt_code] = trace
                    if cdt_code[:2] == 'PH':
                        (event_dict[eventID])[cdt_code] = float(cd_double) * ADCGAIN
                    if cdt_code[:2] == 'IN':
                        (event_dict[eventID])[cdt_code] = float(cd_double) * ((ADCGAIN*2.5)/1000)


def get_hourly_coincidences(detectors, date, hour):
    """
    Get the coincidences for one hour on a given day
    """
    start = str(hour) + ':00:00'
    end = str(hour +1) + ':00:00'
    
    return search_coincidences(detectors, date, start, end)
    

def get_coincidences_per_day(detectors, date):
    """
    Get the coincidences for one hour on a given day
    """
    start = '00:00:00'
    end = '23:59:59'
    
    return search_coincidences(detectors, date, start, end)

