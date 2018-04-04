import os
import random
import time
from urllib.parse import urljoin
from datetime import datetime
import sqlite3

import requests
from robot.libraries.BuiltIn import BuiltIn

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DATABASE_PATH = os.path.join(_BASE_DIR, 'sut/web', 'clients.db')
TIME_SLEEP = 5


class DataBase:
    def __init__(self, db_path=_DATABASE_PATH):
        self._db_path = db_path
        self.connect = None
        self.cursor = None

    def connect_to_db(self):
        self.connect = sqlite3.connect(self._db_path)
        self.cursor = self.connect.cursor()

    def count_row(self, name_tbl):
        query_count = self.cursor.execute('SELECT COUNT(*) FROM {}'.format(name_tbl))
        count,  = query_count.fetchone()
        return count

    def add_row(self, name_tbl, *args):
        self.cursor.execute('INSERT INTO {} VALUES(?,?)'.format(name_tbl), *args)
        self.connect.commit()

    def __del__(self):
        self.connect.close()


class ClientLibrary(DataBase):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'
    HEADERS = {'Content-Type': 'application/json'}

    def __init__(self):
        super(ClientLibrary, self).__init__()

    def get_client_with_positive_balance(self):
        client_balance_query = self.cursor.execute('SELECT * FROM BALANCES'
                                                   ' WHERE BALANCE > 0 LIMIT 1')
        client_balance = client_balance_query.fetchone()
        if client_balance:
            return client_balance
        else:
            client_balance = self.add_client()
        return client_balance

    def add_client(self):
        count_clients_row = self.count_row('CLIENTS')
        client_id_new = count_clients_row + 1
        client_data = (client_id_new, 'Client_{}'.format(client_id_new))
        self.add_row('CLIENTS', client_data)
        client_balance = (client_id_new, 5.0)
        self.add_row('BALANCES', client_balance)
        return client_balance

    def get_client_services(self, url, client_balance):
        id_client, _ = client_balance
        data = {'client_id': id_client}
        url = urljoin(url, 'client/services')
        response = requests.post(url, headers=ClientLibrary.HEADERS, json=data)
        assert response.status_code == 200
        client_services_ = response.json()
        return client_services_

    def get_services(self, url):
        url_services = urljoin(url, 'services')
        response = requests.get(url_services, headers=ClientLibrary.HEADERS)
        services_ = response.json()
        assert response.status_code == 200
        return services_

    def get_unused_services(self, client_services, services):
        if client_services['count'] != services['count']:
            diff_services = [item for item in services['items']
                             if item not in client_services['items']]
            unused_service = random.choice(diff_services)
            assert unused_service
            return unused_service

    def set_client_service(self, url, client_balance, unused_service):
        id_client, _ = client_balance
        id_service = unused_service['id']
        if id_service:
            url = urljoin(url, 'client/add_service')
            data = {'client_id': id_client, 'service_id': id_service}
            response = requests.post(url, headers=ClientLibrary.HEADERS, json=data)
            assert response.status_code == 202
            return response.status_code

    def wait_new_service(self, url, client_balance, unused_service, wait_time):
        id_client, _ = client_balance
        id_service = unused_service['id']
        start_time = datetime.now()
        while True:
            client_services_ = self.get_client_services(url, client_balance)
            id_services_lst = [item['id'] for item in client_services_['items']]
            if id_service in id_services_lst:
                return client_services_
            delta_time = datetime.now() - start_time
            if delta_time.seconds >= wait_time:
                if client_services_['count'] == 0:
                    message = ('The client id {} does not have services. '
                               'The client possible does not exist in database'
                               .format(id_client))
                else:
                    message = 'Something went wrong'
                raise TimeoutError('Exceeded waiting time request... {message}'
                                   .format(message=message))
            time.sleep(TIME_SLEEP)

    def get_client_balance(self, client_balance):
        id_client, _ = client_balance
        query_balance = self.cursor.execute('SELECT BALANCE FROM BALANCES '
                                            'WHERE CLIENTS_CLIENT_ID=?',
                                            (id_client,))
        balance, = query_balance.fetchone()
        assert balance
        return balance

    def compare_start_end_balance(self, client_balance, unused_service, current_balance):
        _, start_balance = client_balance
        cost_service = unused_service['cost']
        balance_end = start_balance - cost_service
        BuiltIn().should_be_equal(balance_end, current_balance,
                                  "Expected status to be '{expected}' but was '{status}'."
                                  .format(expected=balance_end, status=current_balance))
