import os
import random
import time

import sqlite3 as lite
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'web', 'clients.db')


class DataBase:
    def __init__(self, db_path=DATABASE_PATH):
        self.db_path = db_path
        self.conn = None
        self.cur = None

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


class ClientLibrary(DataBase):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self):
        super().__init__()
        self.id_client_positive = None
        self.balance_client_positive = None
        self.client_services = None
        self.services = None
        self.id_service = None
        self.cost_service = None
        self.end_balance = None
        self.headers = {'Content-Type': 'application/json'}
        self._status = None

    def get_connect_to_db(self):
        self.conn = lite.connect(self.db_path)
        self.cur = self.conn.cursor()
        query_balances = self.cur.execute('SELECT * FROM BALANCES')
        balances = query_balances.fetchall()
        if balances:
            self._status = 'SUCCESS'

    def get_balance_positive(self):
        self._status = None
        query_balances = self.cur.execute('SELECT * FROM BALANCES WHERE BALANCE > 0')
        client_tpl = query_balances.fetchone()
        if client_tpl:
            self.id_client_positive, self.balance_client_positive = client_tpl
            self._status = 'SUCCESS'
            return client_tpl
        count_clients_db = self.count_db('CLIENTS')
        client_id_new = count_clients_db + 1
        client_tpl = (client_id_new, 'Client_{}'.format(client_id_new))
        self.add_row('CLIENTS', client_tpl)
        balance_tpl = (client_id_new, 3.5)
        self.add_row('BALANCES', balance_tpl)
        self.id_client_positive, self.balance_client_positive = client_tpl
        client_tpl = query_balances.fetchone()
        query_check_row = self.cur.execute('SELECT BALANCE FROM BALANCES '
                                           'WHERE CLIENTS_CLIENT_ID=?', (client_id_new,))
        check_row, = query_check_row.fetchone()
        if check_row:
            self._status = 'SUCCESS'
            return client_tpl

    def get_client_services(self, port):
        self._status = None
        data = {'client_id': self.id_client_positive}
        url = 'http://localhost:{port}/client/services'.format(port=port)
        response = requests.post(url, headers=self.headers, json=data)
        client_services_ = response.json()
        self.client_services = client_services_
        self._status = str(response.status_code)
        return client_services_

    def get_services(self, port):
        self._status = None
        url = 'http://localhost:{port}/services'.format(port=port)
        response = requests.get(url, headers=self.headers)
        services_ = response.json()
        self.services = services_
        self._status = str(response.status_code)
        return services_

    def get_ex_services(self):
        self._status = None
        if self.client_services['count'] != self.services['count']:
            diff_services = [item for item in self.services['items']
                             if item not in self.client_services['items']]
            ex_service = random.choice(diff_services)
            if ex_service:
                self.id_service = ex_service['id']
                self.cost_service = ex_service['cost']
                self._status = 'SUCCESS'
                return ex_service

    def set_client_service(self, port):
        self._status = None
        if self.id_service is not None:
            url = 'http://localhost:{port}/client/add_service'.format(port=port)
            data = {'client_id': self.id_client_positive, 'service_id': self.id_service}
            response = requests.post(url, headers=self.headers, json=data)
            self._status = str(response.status_code)
            return response.status_code

    def wait_new_service(self, port):
        self._status = None
        time_wait = 0
        while True:
            client_services_ = self.get_client_services(port)
            id_services_lst = [item['id'] for item in client_services_['items']]
            print(id_services_lst)
            if self.id_service in id_services_lst:
                print('Service id = {} added'.format(self.id_service))
                self._status = 'SUCCESS'
                return client_services_
            if time_wait >= 60:
                raise TimeoutError('Exceeded waiting time request...')
            time_wait += 5
            time.sleep(5)

    def get_end_balance(self):
        self._status = None
        query_end_balance = self.cur.execute('SELECT BALANCE FROM BALANCES '
                                             'WHERE CLIENTS_CLIENT_ID=?',
                                             (self.id_client_positive,))
        end_balance, = query_end_balance.fetchone()
        if end_balance:
            self.end_balance = end_balance
            self._status = 'SUCCESS'
            return end_balance

    def compare_start_end_balance(self):
        self._status = None
        if self.end_balance == (self.balance_client_positive - self.cost_service):
            self._status = 'SUCCESS'
        else:
            self._status = 'UNSUCCESS'

    def status_should_be(self, expected_status):
        if expected_status != self._status:
            raise AssertionError("Expected status to be '%s' but was '%s'."
                                 % (expected_status, self._status))
