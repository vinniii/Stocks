import sqlite3 as dEntry


class CreateDB:
    def __init__(self):
        self.con = dEntry.connect('dataRecords.db')
        self.cur = self.con.cursor()
        self.createTable(self.con)
        print(self.con)
    
    def createTable(self, con):
        try:
            self.cur.execute("""CREATE TABLE IF NOT EXISTS RECORDS
                     (stock, time, quantity, type, price)""")
        except Exception as e:
            print(e)