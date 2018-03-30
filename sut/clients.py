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
        query_count = self.cur.execute('SELECT COUNT(*) FROM {}'.format(name_tbl))
        count,  = query_count.fetchone()
        return count

    def add_row(self, name_tbl, *args):
        self.cur.execute('INSERT INTO {} VALUES(?,?)'.format(name_tbl), *args)
        self.conn.commit()

    def close_db(self):
        self.conn.close()

    def __del__(self):
        self.close_db()


class Client:
    def __init__(self):
        self._id_client_positive = ''

    def get_balance_positive(self):
        db = DataBase()
        query_balances = db.cur.execute('SELECT * FROM BALANCES WHERE BALANCE > 0')
        client_tpl = query_balances.fetchone()
        if client_tpl:
            self._id_client_positive = client_tpl[0]
            return client_tpl
        count_cliens_db = db.count_db('CLIENTS')
        client_id_new = count_cliens_db + 1
        client_tpl = (client_id_new, 'Client_{}'.format(client_id_new))
        db.add_row('CLIENTS', client_tpl)
        balance_tpl = (client_id_new, 10.5)
        db.add_row('BALANCES', balance_tpl)
        self._id_client_positive = client_id_new
        return client_tpl


