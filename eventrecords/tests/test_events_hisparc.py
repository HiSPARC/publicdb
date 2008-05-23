#!/usr/bin/python

from MySQLdb import connect
from random import randint

dest = {
    'host': 'localhost',
    'user': 'hisparc',
    'db': 'events_hisparc',
    'password' : 'Crapsih',
    'port': 3306,
}

N = 10**1
M = 10**5

class test:
    def __init__(self, dest):
        self.connect(dest)
        return

    def connect(self, dest):
        self.db = connect(
            dest['host'], dest['user'], dest['password'], dest['db'],
            dest['port'],
        )

        self.cursor = self.db.cursor()

        return

    def test(self):
        self.set_table_engine('MyISAM')

        self.print_data_size()
        self.insert_record(M)

        for i in range(N-1):
            self.print_data_size()
            self.insert_record(M)
            self.drop_first_traces(M)
            self.optimize_table()

        self.print_data_size()
        return

    def set_table_engine(self, engine):
        sql = "ALTER TABLE events_hisparc ENGINE=%s" % engine
        self.transaction(sql, True)
        return

    def insert_record(self, num = 1):
        for i in range(num):
            sql  = "INSERT "
            sql += "events_hisparc (gpsevent_id, adcevent_id, "
            sql += "softwaredeadtime, gpsreadoutdelay, trace1, trace2) "
            sql += "VALUES ("
            sql += "'%s', " % 1234567
            sql += "'%s', " % 1234567
            sql += "'%s', " % 123.456
            sql += "'%s', " % 123.456
            sql += "'%s', " % (10**4 * 'x')
            sql += "'%s')"  % (10**4 * 'x')
            self.transaction(sql)

        self.commit()
        return

    def delete_random_record(self):
        sql = "SELECT COUNT(*) FROM events_hisparc"
        self.cursor.execute(sql)
        numrows = self.cursor.fetchone()[0]

        row = randint(0,numrows-1)

        sql = "SELECT event_id FROM events_hisparc LIMIT %d, 1" % row
        self.cursor.execute(sql)
        id = self.cursor.fetchone()[0]

        sql = "DELETE FROM events_hisparc WHERE event_id = %d" % id
        self.transaction(sql, True)

        return

    def drop_first_traces(self, num = 1):
        sql  = "SELECT event_id FROM events_hisparc "
        sql += "WHERE trace1 IS NOT NULL LIMIT %d " % num
        self.cursor.execute(sql)
        
        for id, in self.cursor.fetchall():
            sql  = "UPDATE events_hisparc "
            sql += "SET trace1 = NULL, trace2 = NULL "
            sql += "WHERE event_id = %d " % id
            self.transaction(sql)

        self.commit()
        return

    def optimize_table(self):
        sql = "OPTIMIZE TABLE events_hisparc"
        self.transaction(sql, True)
        return

    def print_data_size(self):
        for i in self.get_data_size():
            print i,
        print
        return

    def get_data_size(self):
        sql = "SELECT COUNT(*) FROM events_hisparc"
        self.cursor.execute(sql)
        rows = self.cursor.fetchone()[0]

        sql = "SHOW TABLE STATUS"
        self.cursor.execute(sql)
        datasize = self.cursor.fetchone()[6]

        return rows, datasize


    def transaction(self, sql, commit = False):
        self.cursor.execute(sql)

        if commit:
            self.commit()

        return

    def commit(self):
        self.cursor.execute("COMMIT")
        return


if __name__ == '__main__':
    app = test(dest)
    app.test()
