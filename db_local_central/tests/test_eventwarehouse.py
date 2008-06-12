#!/usr/bin/python

from MySQLdb import connect
import re
from optparse import OptionParser

dest = {
    'host': 'localhost',
    'user': 'hisparc',
    'db': 'eventwarehouse',
    'password' : 'Crapsih',
    'port': 3306,
}

class test:
    nullstring = re.compile("''|'None'")
    event_id = 1

    def __init__(self, dest, engine, N, M):
        self.engine = engine
        self.N = N
        self.M = M

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
        self.set_table_engine(self.engine)

        self.print_data_size()
        self.insert_record(self.M)

        for i in range(self.N-1):
            self.print_data_size()
            self.insert_record(self.M)
            self.drop_first_traces(self.M)

        self.print_data_size()
        return

    def set_table_engine(self, engine):
        sql = "ALTER TABLE eventdata ENGINE=%s" % engine
        self.transaction(sql, True)
        return

    def insert_record(self, num = 1):
        for i in range(num):
            self.insert_row(1, self.event_id, 4, None, None, None)
            self.insert_row(2, self.event_id, 4, None, None, None)
            self.insert_row(3, self.event_id, None, 4.4, None, None)
            self.insert_row(4, self.event_id, None, 4.4, None, None)
            self.insert_row(5, self.event_id, None, None, None, 10**4 * 'x')
            self.insert_row(6, self.event_id, None, None, None, 10**4 * 'x')
            self.event_id += 1

        self.commit()
        return

    def insert_row(self, eventdatatype_id, event_id, integervalue,
        doublevalue, textvalue, blobvalue):

        sql  = "INSERT eventdata "
        sql += "(eventdatatype_id, event_id, integervalue, "
        sql += "doublevalue, textvalue, blobvalue) "
        sql += "VALUES ("
        sql += "'%s', " % eventdatatype_id
        sql += "'%s', " % event_id
        sql += "'%s', " % integervalue
        sql += "'%s', " % doublevalue
        sql += "'%s', " % textvalue
        sql += "'%s')"  % blobvalue
        self.transaction(sql)
       

    def drop_first_traces(self, num = 1):
        sql  = "SELECT event_id FROM eventdata "
        sql += "WHERE eventdatatype_id = 5 "
        sql += "AND blobvalue IS NOT NULL LIMIT %d " % num
        self.cursor.execute(sql)
        
        for id, in self.cursor.fetchall():
            sql  = "DELETE FROM eventdata "
            sql += "WHERE event_id = %d " % id
            sql += "AND (eventdatatype_id = 5 OR eventdatatype_id = 6)"
            self.transaction(sql)

        self.commit()
        return

    def print_data_size(self):
        for i in self.get_data_size():
            print i,
        print
        return

    def get_data_size(self):
        sql = "SELECT COUNT(*) FROM eventdata"
        self.cursor.execute(sql)
        rows = self.cursor.fetchone()[0]

        sql = "SHOW TABLE STATUS"
        self.cursor.execute(sql)
        datasize = self.cursor.fetchone()[6]

        return rows, datasize


    def transaction(self, sql, commit = False):
        sql = self.nullstring.sub("NULL", sql)
        self.cursor.execute(sql)

        if commit:
            self.commit()

        return

    def commit(self):
        self.cursor.execute("COMMIT")
        return


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-e", "--engine", dest="engine",
                      help="MySQL engine (MyISAM, InnoDB)")
    parser.add_option("-n", dest="N", type="int",
                      help="Number of transactions")
    parser.add_option("-m", dest="M", type="int",
                      help="Number of events per transaction")
    (options, args) = parser.parse_args()

    if not options.engine or not options.N or not options.M:
        parser.error("All options are required!")

    app = test(dest, options.engine, options.N, options.M)
    app.test()
