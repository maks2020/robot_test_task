import os
import random
import time
from urllib.parse import urljoin

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

    def count_db(self, name_tbl):
        query_count = self.cursor.execute('SELECT COUNT(*) FROM {}'.format(name_tbl))
        count,  = query_count.fetchone()
        return count

    def add_row(self, name_tbl, *args):
        self.cursor.execute('INSERT INTO {} VALUES(?,?)'.format(name_tbl), *args)
        self.connect.commit()

    def close_db(self):
        self.connect.close()

    def __del__(self):
        self.close_db()


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
        self._end_balance = None
        self._status = None

    def connect_to_db(self):
        self.connect = sqlite3.connect(self._db_path)
        self.cursor = self.connect.cursor()
        try:
            self.cursor.execute('SELECT * FROM BALANCES')
        except sqlite3.OperationalError:
            raise sqlite3.OperationalError('not connect database for task')

    def get_balance_positive(self):
        self._status = None
        client_balance = self.cursor.execute('SELECT * FROM BALANCES WHERE BALANCE > 0 LIMIT 1')
        balance_data = client_balance.fetchone()
        if balance_data:
            self._id_client_positive, self._balance_client_positive = balance_data
            return balance_data
        else:
            count_clients_db = self.count_db('CLIENTS')
            client_id_new = count_clients_db + 1
            client_data = (client_id_new, 'Client_{}'.format(client_id_new))
            self.add_row('CLIENTS', client_data)
            balance_data = (client_id_new, 5.0)
            self.add_row('BALANCES', balance_data)
            self._id_client_positive, self._balance_client_positive = balance_data
        return balance_data

    def get_client_services(self, url):
        data = {'client_id': self._id_client_positive}
        url = urljoin(url, 'client/services')
        response = requests.post(url, headers=ClientLibrary.HEADERS, json=data)
        client_services_ = response.json()
        self._client_services = client_services_
        assert response.status_code == 200
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

    def set_client_service(self, port):
        self._status = None
        if self._id_service is not None:
            url = 'http://localhost:{port}/client/add_service'.format(port=port)
            data = {'client_id': self._id_client_positive, 'service_id': self._id_service}
            response = requests.post(url, headers=ClientLibrary.HEADERS, json=data)
            self._status = str(response.status_code)
            return response.status_code

    def wait_new_service(self, url):
        self._status = None
        time_wait = 0
        while True:
            client_services_ = self.get_client_services(url)
            id_services_lst = [item['id'] for item in client_services_['items']]
            if self._id_service in id_services_lst:
                print('Service id = {} added'.format(self._id_service))
                self._status = 'SUCCESS'
                return client_services_
            if time_wait >= 60:
                raise TimeoutError('Exceeded waiting time request...')
            time_wait += 5
            time.sleep(5)

    def get_end_balance(self):
        self._status = None
        query_end_balance = self.cursor.execute('SELECT BALANCE FROM BALANCES '
                                             'WHERE CLIENTS_CLIENT_ID=?',
                                             (self._id_client_positive,))
        end_balance, = query_end_balance.fetchone()
        if end_balance:
            self._end_balance = end_balance
            self._status = 'SUCCESS'
            return end_balance

    def compare_start_end_balance(self):
        self._status = None
        if self._end_balance == (self._balance_client_positive - self._cost_service):
            self._status = 'SUCCESS'
        else:
            self._status = 'UNSUCCESS'

    def status_should_be(self, expected_status):
        BuiltIn().run_keyword('Should Be Equal', expected_status, self._status,
                              "Expected status to be '{expected}' but was '{status}'."
                              .format(expected=expected_status, status=self._status))


if __name__ == '__main__':
    client = ClientLibrary()
    client.connect_to_db()
    print(client.get_balance_positive())
    print(client.get_client_services('http://localhost:5000'))
    print(client.get_services('http://localhost:5000'))
    print(client.get_ex_services())
    print(client.set_client_service(5000))
    print(client.wait_new_service('http://localhost:5000'))