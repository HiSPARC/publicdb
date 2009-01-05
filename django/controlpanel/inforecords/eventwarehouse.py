from django.conf import settings
import MySQLdb

def update_station_password(station_id, password):
    """Insert or update a station password into the eventwarehouse

    This function will first check if a password is already stored in the
    eventwarehouse. If so, update the password. If not, insert a new entry into
    the eventwarehouse containing station_id and password.

    """
    conn = eventwarehouse_connection()
    cursor = conn.cursor()

    sql = "SELECT COUNT(*) FROM stationpasswords WHERE stationnumber=%d" % \
          station_id
    cursor.execute(sql)

    if cursor.fetchone()[0]:
        sql = "UPDATE stationpasswords SET password='%s' WHERE " \
              "stationnumber=%d" % (password, station_id)
    else:
        sql = "INSERT INTO stationpasswords(stationnumber, password) " \
              "VALUES(%d, '%s')" % (station_id, password)
    cursor.execute(sql)
    conn.commit()

def remove_station_password(station_id):
    """Remove a station password from the eventwarehouse

    This function will remove a station password from the eventwarehouse.

    """
    conn = eventwarehouse_connection()
    cursor = conn.cursor()

    sql = "DELETE FROM stationpasswords WHERE stationnumber=%d" % station_id
    cursor.execute(sql)
    conn.commit()

def eventwarehouse_connection():
    db = MySQLdb.connect(settings.EVENTWAREHOUSE_HOST,
                         settings.EVENTWAREHOUSE_USER,
                         settings.EVENTWAREHOUSE_PASSWORD,
                         settings.EVENTWAREHOUSE_NAME)
    return db
