import os
import random
import time
from urllib.parse import urljoin
from datetime import datetime

import sqlite3
import requests
from robot.libraries.BuiltIn import BuiltIn

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATABASE_PATH = os.path.join(_BASE_DIR, 'web', 'clients.db')


class DataBase:
    def __init__(self, db_path=_DATABASE_PATH):
        self._db_path = db_path
        self.connect = None
        self.cursor = None

    def count_row(self, name_tbl):
        query_count = self.cursor.execute('SELECT COUNT(*) FROM {}'.format(name_tbl))
        count,  = query_count.fetchone()
        return count

    def add_client(self, *args):
        self.cursor.execute('INSERT INTO CLIENTS VALUES(?,?)', *args)
        self.connect.commit()

    def add_client_balance(self, *args):
        self.cursor.execute('INSERT INTO BALANCES VALUES(?,?)', *args)
        self.connect.commit()

    def __del__(self):
        self.connect.close()


class ClientLibrary(DataBase):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    HEADERS = {'Content-Type': 'application/json'}

    def __init__(self):
        super(ClientLibrary, self).__init__()
        self._id_client_positive = None
        self._balance_client_positive = None
        self._client_services = None
        self._services = None
        self._id_service = None
        self._cost_service = None
        self._balance = None
        self._status = None

    def connect_to_db(self):
        self.connect = sqlite3.connect(self._db_path)
        self.cursor = self.connect.cursor()
        try:
            self.cursor.execute('SELECT * FROM BALANCES')
        except sqlite3.OperationalError:
            raise sqlite3.OperationalError('not connect database for task')

    def get_client_balance_positive(self):
        self._status = None
        client_balance_query = self.cursor.execute('SELECT * FROM BALANCES'
                                                   ' WHERE BALANCE > 0 LIMIT 1')
        client_balance = client_balance_query.fetchone()
        if client_balance:
            self._id_client_positive, self._balance_client_positive = client_balance
            return client_balance
        else:
            count_clients_row = self.count_row('CLIENTS')
            client_id_new = count_clients_row + 1
            client_data = (client_id_new, 'Client_{}'.format(client_id_new))
            self.add_client(client_data)
            client_balance = (client_id_new, 5.0)
            self.add_client_balance(client_balance)
            self._id_client_positive, self._balance_client_positive = client_balance
        return client_balance

    def get_client_services(self, url):
        data = {'client_id': self._id_client_positive}
        url = urljoin(url, 'client/services')
        response = requests.post(url, headers=ClientLibrary.HEADERS, json=data)
        assert response.status_code == 200
        client_services_ = response.json()
        self._client_services = client_services_
        return client_services_

    def get_services(self, url):
        url_services = urljoin(url, 'services')
        response = requests.get(url_services, headers=ClientLibrary.HEADERS)
        services_ = response.json()
        self._services = services_
        assert response.status_code == 200
        return services_

    def get_unused_services(self):
        try:
            assert self._client_services
        except AssertionError:
            raise ValueError('client services not define')
        try:
            assert self._services
        except AssertionError:
            raise ValueError('services not define')
        if self._client_services['count'] != self._services['count']:
            diff_services = [item for item in self._services['items']
                             if item not in self._client_services['items']]
            unused_service = random.choice(diff_services)
            assert unused_service
            self._id_service = unused_service['id']
            self._cost_service = unused_service['cost']
            return unused_service

    def set_client_service(self, url):
        if self._id_service:
            url = urljoin(url, 'client/add_service')
            data = {'client_id': self._id_client_positive, 'service_id': self._id_service}
            response = requests.post(url, headers=ClientLibrary.HEADERS, json=data)
            assert response.status_code == 202
            return response.status_code

    def wait_new_service(self, url):
        start_time = datetime.now()
        while True:
            delta_time = datetime.now() - start_time
            if delta_time.seconds >= 60:
                raise TimeoutError('Exceeded waiting time request...')
            client_services_ = self.get_client_services(url)
            id_services_lst = [item['id'] for item in client_services_['items']]
            if self._id_service in id_services_lst:
                print('Service id = {} added'.format(self._id_service))
                return client_services_
            time.sleep(5)

    def get_balance(self):
        query_balance = self.cursor.execute('SELECT BALANCE FROM BALANCES '
                                            'WHERE CLIENTS_CLIENT_ID=?',
                                            (self._id_client_positive,))
        balance, = query_balance.fetchone()
        assert balance
        self._balance = balance
        return balance

    def compare_start_end_balance(self):
        balance_end = self._balance_client_positive - self._cost_service
        BuiltIn().run_keyword('Should Be Equal', balance_end, self._balance,
                              "Expected status to be '{expected}' but was '{status}'."
                              .format(expected=balance_end, status=self._balance))
