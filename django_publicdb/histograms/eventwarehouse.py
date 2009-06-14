from django.conf import settings
import MySQLdb

def eventwarehouse_connection():
    port = settings.EVENTWAREHOUSE_PORT
    if not port:
        port = 0
    else:
        port = int(port)

    db = MySQLdb.connect(settings.EVENTWAREHOUSE_HOST,
                         settings.EVENTWAREHOUSE_USER,
                         settings.EVENTWAREHOUSE_PASSWORD,
                         settings.EVENTWAREHOUSE_NAME,
                         port=port)
    return db

def check_for_new_events(last_event_id):
    conn = eventwarehouse_connection()
    cursor = conn.cursor()

    sql = "SELECT event_id FROM event ORDER BY event_id DESC LIMIT 1"
    cursor.execute(sql)
    new_last_event_id = cursor.fetchone()[0]

    sql = "SELECT station_id, date FROM event JOIN eventtype " \
          "USING (eventtype_id) WHERE uploadcode = 'CIC' AND event_id > %d " \
          "GROUP BY station_id, date" % last_event_id
    cursor.execute(sql)
    results = cursor.fetchall()

    return new_last_event_id, results

def get_eventtime_histogram(station_id, date):
    conn = eventwarehouse_connection()
    cursor = conn.cursor()
    sql = "SELECT HOUR(time), COUNT(*) FROM event JOIN eventtype "\
          "USING(eventtype_id) WHERE uploadcode = 'CIC' AND station_id = %d " \
          "AND date = '%s' GROUP BY HOUR(time)" % (station_id, date)
    cursor.execute(sql)
    results = cursor.fetchall()

    data = {}
    for result in results:
        hour, count = result
        data[hour] = count

    return data

def get_pulseheights(station_id, date):
    conn = eventwarehouse_connection()
    cursor = conn.cursor()
    sql = "SELECT cdt.uploadcode, cd.doublevalue FROM event e " \
          "JOIN eventtype et USING(eventtype_id) " \
          "JOIN calculateddata cd USING(event_id) " \
          "JOIN calculateddatatype cdt USING(calculateddatatype_id) " \
          "WHERE et.uploadcode = 'CIC' AND station_id = %d AND date = '%s' " \
          "AND cdt.uploadcode IN ('PH1', 'PH2', 'PH3', 'PH4')" % \
          (station_id, date)
    cursor.execute(sql)

    values = [[], [], [], []]
    for type, value in cursor.fetchall():
        scint_num = int(type[2])-1
        values[scint_num].append(value)

    return values

def get_pulseintegrals(station_id, date):
    conn = eventwarehouse_connection()
    cursor = conn.cursor()
    sql = "SELECT cdt.uploadcode, cd.doublevalue FROM event e " \
          "JOIN eventtype et USING(eventtype_id) " \
          "JOIN calculateddata cd USING(event_id) " \
          "JOIN calculateddatatype cdt USING(calculateddatatype_id) " \
          "WHERE et.uploadcode='CIC' AND station_id = %d AND date = '%s' " \
          "AND cdt.uploadcode IN ('IN1', 'IN2', 'IN3', 'IN4')" % \
          (station_id, date)
    cursor.execute(sql)

    values = [[], [], [], []]
    for type, value in cursor.fetchall():
        scint_num = int(type[2])-1
        values[scint_num].append(value)

    return values
