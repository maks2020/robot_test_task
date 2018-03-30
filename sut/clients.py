import os
import sqlite3 as lite


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'web', 'clients.db')


class DataBase:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = lite.connect(self.db_path)
        self.cur = self.conn.cursor()

    def connect(self):
        conn = lite.connect(self.db_path)
        cur = conn.cursor()
        return conn, cur

    def count_db(self, name_tbl):
        query_count = self.cur.execute('select count(*) from {}'.format(name_tbl))
        count,  = query_count.fetchone()
        return count

    def add_row(self, *args, row_id=None):
        if row_id is not None:
            self.cur.execute('insert into BALANCES() values(?,?)', args)
            self.conn.commit()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()



