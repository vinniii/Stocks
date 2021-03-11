import sqlite3 as dEntry
from datetime import datetime, timedelta

from scipy.stats.mstats import gmean

import create_database


class RecordTrade:
    def __init__(self):
        self.status = False
        self.dbRecord = create_database.CreateDB()

    def _add_record_entry(self, stock, time_stamp, quantity, typeStock, price):
        try:
            # Adding one entry at a time, We can extend this to adding multiple entries at a time
            # by using self.dbRecord.cur.executemany
            self.dbRecord.cur.execute("""INSERT INTO RECORDS (stock, time, quantity, type, price)
            values(?, ?, ?, ?, ?)""", (stock, time_stamp, quantity, typeStock, price))
            self.dbRecord.con.commit()
            self.status = True
        except dEntry.DatabaseError as e:
            self.status = False
            print(e)

    def _get_volume_weighted_average(self, stock):
        # We can even use fetchall and query here 
        prevTime = datetime.now() - timedelta(minutes=5)
        prev = prevTime.strftime("%d/%m/%Y%H/%M/%S")
        all_entries = []
        # Getting all records of a particular stock
        try:
            query = ("SELECT * FROM RECORDS WHERE stock = \"" + stock + "\"")
            self.dbRecord.cur.execute(query)
            result = self.dbRecord.cur.fetchall()
        except Exception as e:
            print("Database connectivity error" + str(e))
            return None
        # All entries of a particular stock in result
        for row in result:
            if row[1] > prev:
                all_entries.append(row)
        print(self.calcVolume(all_entries))
        return self.calcVolume(all_entries)

    def calcVolume(self, entries):
        v = 0.0
        pv = 0.0
        for row in range(len(entries)):
            pv = pv + (float(entries[row][2]) * float(entries[row][4]))
            v = v + float(entries[row][2])
        try:
            return (pv / v)
        except ZeroDivisionError as e:
            print(e)
            return 0.0

    def _all_shared_index(self):
        try:
            # Getting data of weighted Volume average of less than 5 mins
            wvl = []
            query = ("SELECT DISTINCT stock FROM RECORDS")
            self.dbRecord.cur.execute(query)
            result = self.dbRecord.cur.fetchall()
            print(result)
            for stock_record in range(len(result)):
                print(result[stock_record][0])
                w = self._get_volume_weighted_average(result[stock_record][0])
                wvl.append(w)
            res = gmean(wvl)
            return res
        except Exception as e:
            print("Database connectivity error" + str(e))
            return None
