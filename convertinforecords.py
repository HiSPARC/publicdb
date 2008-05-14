#!/usr/bin/python

from MySQLdb import connect
import re

src = {
    'host': 'oust',
    #'host': '127.0.0.1',
    'user': 'webread',
    'db': 'hisparc',
    'password': '',
    'port': 3306,
    #'port': 3307,
}
dest = {
    'host': 'localhost',
    'user': 'hisparc',
    'db': 'hisparc',
    'password' : 'Crapsih',
    'port': 3306,
}

class convert:
    nullstring = re.compile("''|'None'")
    prefix_re = re.compile("([a-z ]*)([A-Z][A-Za-z ]*)")

    def __init__(self, src, dest):
        self.connect(src, dest)
        return

    def connect(self, src, dest):
        self.src_db = connect(
            src['host'], src['user'], src['password'], src['db'],
            src['port'],
        )
        self.dest_db = connect(
            dest['host'], dest['user'], dest['password'], dest['db'],
            dest['port'],
        )

        self.src_cursor = self.src_db.cursor()
        self.dest_cursor = self.dest_db.cursor()

        return

    def convert(self):
        self.convert_personen()
        self.convert_clusters()
        self.convert_lokaties()
        self.convert_detectoren()
        
        self.src_cursor.close()
        self.dest_cursor.close()
        return

    def convert_personen(self):
        sql  = "SELECT "
        sql += "persFun, persTit, persVoornaam, persAchternaam, "
        sql += "persURL, persMail, persTelW, persTelP "
        sql += "FROM personen"
        self.src_cursor.execute(sql)

        for r in self.src_cursor.fetchall():
            contactposition_id, title, firstname, lastname, url, \
            email, phone_work, phone_home = r

            if contactposition_id == 0: contactposition_id = ''

            p = self.prefix_re.search(lastname)
            prefix = p.group(1).strip()
            lastname = p.group(2)

            sql  = "INSERT "
            sql += "contact (contactposition_id, title, firstname, "
            sql += "prefix, lastname, url, email, phone_work, "
            sql += "phone_home) "
            sql += "VALUES ("
            sql += "'%s', " % contactposition_id
            sql += "'%s', " % title
            sql += "'%s', " % firstname
            sql += "'%s', " % prefix
            sql += "'%s', " % lastname
            sql += "'%s', " % url
            sql += "'%s', " % email
            sql += "'%s', " % phone_work
            sql += "'%s')"  % phone_home

            self.dest_transaction(sql)

        self.dest_commit()

        return

    def convert_clusters(self):
        sql = 'SELECT clusNaam, clusURL FROM clusters'
        self.src_cursor.execute(sql)

        for r in self.src_cursor.fetchall():
            name, url = r

            if name == 'ONBEKEND' or name == 'Wachtlijst': continue

            sql  = "INSERT cluster (name, url) VALUES ('%s', '%s')" \
                % (name, url)
            self.dest_transaction(sql)

        self.dest_commit()
        
        return

    def convert_lokaties(self):
        sql  = "SELECT "
        sql += "clusNaam, locNaam, locURL, locAdres, locPostcode, "
        sql += "locPostbus, locPostbusPostcode, locStad, locTel, "
        sql += "locFax, locMail, locStat "
        sql += "FROM lokaties JOIN clusters WHERE clusId = locClusId"
        self.src_cursor.execute(sql)

        for r in self.src_cursor.fetchall():
            clusname, name, url , address, postalcode, pobox, \
            pobox_postalcode, city, phone, fax, email, status = r
            country = 'Netherlands'
            if status == 0: status = ''

            if name == 'ONBEKEND': continue

            # ugly hacks start here
            if address == '': address = 'zzz'
            if postalcode == '': postalcode = 'zzz'
            if city == '': city = 'zzz'
            # end of ugly hacks

            cluster_id = self.get_cluster_id(clusname)

            sql  = "INSERT "
            sql += "organization (name, url) "
            sql += "VALUES ("
            sql += "'%s', " % name
            sql += "'%s')"  % url
            self.dest_transaction(sql, True)

            organization_id = self.get_organization_id(name)

            sql  = "INSERT "
            sql += "location (name, organization_id, cluster_id, "
            sql += "locationstatus_id, address, postalcode, pobox, "
            sql += "pobox_postalcode, city, country, phone, fax, url, "
            sql += "email) "
            sql += "VALUES ("
            sql += "'%s', " % name
            sql += "'%s', " % organization_id
            sql += "'%s', " % cluster_id
            sql += "'%s', " % status
            sql += "'%s', " % address
            sql += "'%s', " % postalcode
            sql += "'%s', " % pobox
            sql += "'%s', " % pobox_postalcode
            sql += "'%s', " % city
            sql += "'%s', " % country
            sql += "'%s', " % phone
            sql += "'%s', " % fax
            sql += "'%s', " % url
            sql += "'%s')"  % email
            self.dest_transaction(sql, True)

        return

    def convert_detectoren(self):
        sql  = "SELECT detNum, locNaam, detStartDat, detEindDat, "
        sql += "detLongWGS84, detLatWGS84, detHeightWGS84, detPass "
        sql += "FROM detectoren JOIN lokaties WHERE detLocId = LocId"
        self.src_cursor.execute(sql)

        for r in self.src_cursor.fetchall():
            number, locname, startdate, enddate, longitude, latitude, \
            height, password = r
            if not startdate: startdate = '2000-1-1'

            # status offline
            status = '3'

            location_id = self.get_location_id(locname)

            sql  = "INSERT station (location_id, number) "
            sql += "VALUES ('%s', '%s')" % (location_id, number)
            self.dest_transaction(sql, True)

            station_id = self.get_station_id(number)

            sql  = "INSERT detector_hisparc (station_id, status_id, "
            sql += "startdate, enddate, latitude, longitude, height, "
            sql += "password) "
            sql += "VALUES("
            sql += "'%s', " % station_id
            sql += "'%s', " % status
            sql += "'%s', " % startdate
            sql += "'%s', " % enddate
            sql += "'%s', " % latitude
            sql += "'%s', " % longitude
            sql += "'%s', " % height
            sql += "'%s')"  % password
            self.dest_transaction(sql, True)

        return

    def get_cluster_id(self, name):
        sql = "SELECT cluster_id FROM cluster WHERE name = '%s'" % name
        self.dest_cursor.execute(sql)

        return self.dest_cursor.fetchone()[0]

    def get_organization_id(self, name):
        sql  = "SELECT organization_id FROM organization "
        sql += "WHERE name = '%s'" % name
        self.dest_cursor.execute(sql)

        return self.dest_cursor.fetchone()[0]
    
    def get_location_id(self, name):
        sql  = "SELECT location_id FROM location "
        sql += "WHERE name = '%s'" % name
        self.dest_cursor.execute(sql)

        return self.dest_cursor.fetchone()[0]

    def get_station_id(self, number):
        sql  = "SELECT station_id FROM station "
        sql += "WHERE number = '%s'" % number
        self.dest_cursor.execute(sql)

        return self.dest_cursor.fetchone()[0]

    def dest_transaction(self, sql, commit = False):
        sql = self.nullstring.sub("NULL", sql)
        self.dest_cursor.execute(sql)

        if commit:
            self.dest_commit()

        return

    def dest_commit(self):
        self.dest_cursor.execute("COMMIT")
        return


if __name__ == '__main__':
    app = convert(src, dest)
    app.convert()
