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

    def connect(self):
        self.conn = lite.connect(self.db_path)
        self.cur = self.conn.cursor()

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
        self.db = None
        self.cur = None
        self.id_client_positive = None
        self.balance_client_positive = None
        self.client_services = None
        self.services = None
        self.id_service = None
        self.cost_service = None
        self.end_balance = None
        self.headers = {'Content-Type': 'application/json'}

    def get_connect_to_db(self):
        self.db = DataBase()
        self.db.connect()
        self.cur = self.db.cur

    def get_balance_positive(self):
        query_balances = self.cur.execute('SELECT * FROM BALANCES WHERE BALANCE > 0')
        client_tpl = query_balances.fetchone()
        if client_tpl:
            self.id_client_positive, self.balance_client_positive = client_tpl
            return client_tpl
        count_clients_db = self.db.count_db('CLIENTS')
        client_id_new = count_clients_db + 1
        client_tpl = (client_id_new, 'Client_{}'.format(client_id_new))
        self.db.add_row('CLIENTS', client_tpl)
        balance_tpl = (client_id_new, 10.5)
        self.db.add_row('BALANCES', balance_tpl)
        self.id_client_positive, self.balance_client_positive = client_tpl
        return client_tpl

    def get_client_services(self, port):
        data = {'client_id': self.id_client_positive}
        url = 'http://localhost:{port}/client/services'.format(port=port)
        response = requests.post(url, headers=self.headers, json=data)
        client_services_ = response.json()
        self.client_services = client_services_
        return client_services_

    def get_services(self, port):
        url = 'http://localhost:{port}/services'.format(port=port)
        response = requests.get(url, headers=self.headers)
        services_ = response.json()
        self.services = services_
        return services_

    def get_ex_services(self):
        if self.client_services['count'] != self.services['count']:
            diff_services = [item for item in self.services['items']
                             if item not in self.client_services['items']]
            ex_service = random.choice(diff_services)
            self.id_service = ex_service['id']
            self.cost_service = ex_service['cost']
            return ex_service

    def set_client_service(self, port):
        if self.id_service is not None:
            url = 'http://localhost:{port}/client/add_service'.format(port=port)
            data = {'client_id': self.id_client_positive, 'service_id': self.id_service}
            response = requests.post(url, headers=self.headers, json=data)
            return response.status_code

    def wait_new_service(self, port):
        time_wait = 0
        while True:
            client_services_ = self.get_client_services(port)
            id_services_lst = [item['id'] for item in client_services_['items']]
            print(id_services_lst)
            if self.id_service in id_services_lst:
                print('Service id = {} added'.format(self.id_service))
                return client_services_
            if time_wait >= 60:
                raise TimeoutError('Exceeded waiting time request...')
            time_wait += 5
            time.sleep(5)

    def get_end_balance(self):
        query_end_balance = self.cur.execute('SELECT BALANCE FROM BALANCES '
                                             'WHERE CLIENTS_CLIENT_ID=?',
                                             (self.id_client_positive,))
        end_balance, = query_end_balance.fetchone()
        self.end_balance = end_balance
        return end_balance

    def compare_start_end_balance(self):
        if self.end_balance == (self.balance_client_positive - self.cost_service):
            return True
        else:
            raise ValueError('Is not valid end balance')


if __name__ == '__main__':
    client = Client()
    client.get_connect_to_db()
    balance_positive = client.get_balance_positive()
    print(balance_positive)
    client_services_ = client.get_client_services(5000)
    services = client.get_services(5000)
    client.get_ex_services()
    print(client.id_service)
    client.set_client_service(5000)
    client.wait_new_service(5000)
    client.get_end_balance()
    print(client.end_balance)
    print(client.compare_start_end_balance())

