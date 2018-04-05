import random
import time
from urllib.parse import urljoin
import datetime as dt
import sqlite3

import requests

_TIME_SLEEP = 5
_HEADERS = {'Content-Type': 'application/json'}


class DataBaseLibrary:
    """The library provides work with the database"""
    def __init__(self):
        self._connect = None
        self.cursor = None

    def connect_to_db(self, db_path):
        """Connect to database"""
        self._connect = sqlite3.connect(db_path)
        self.cursor = self._connect.cursor()

    def close_db(self):
        """Close connection with database"""
        self._connect.close()
        self.cursor = None
        self._connect = None


class ClientLibrary(DataBaseLibrary):
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, host, port):
        super(ClientLibrary, self).__init__()
        self.host = host
        self.port = port

    def url_join(self, path):
        return urljoin('{host}:{port}'
                       .format(host=self.host, port=self.port), path)

    def take_add_client_with_positive_balance(self, balance_for_new_client):
        """Return id and balance of client with positive balance or
        create new client if not exist"""
        client_balance_query = self.cursor.execute('SELECT * FROM BALANCES'
                                                   ' WHERE BALANCE > 0 LIMIT 1')
        client_with_balance = client_balance_query.fetchone()
        if not client_with_balance:
            client_with_balance = self.add_client(balance_for_new_client)
        return client_with_balance

    def add_client(self, balance_for_new_client):
        """Add client into database and return client_id, balance"""
        self.cursor.execute('INSERT INTO CLIENTS (CLIENT_NAME) VALUES(?)',
                            ('Ringo',))
        id_client = self.cursor.lastrowid
        client_with_balance = (id_client, balance_for_new_client)
        self.cursor.execute('INSERT INTO BALANCES VALUES(?,?)',
                            client_with_balance)
        self._connect.commit()
        return client_with_balance

    def get_client_services(self, client_id):
        """Return the dictionary services of client"""
        data = {'client_id': client_id}
        url = self.url_join('client/services')
        response = requests.post(url, headers=_HEADERS, json=data)
        assert response.status_code == 200
        client_services_ = response.json()
        return client_services_

    def get_services(self):
        """Return the dictionary of available services"""
        url = self.url_join('services')
        response = requests.get(url, headers=_HEADERS)
        services_ = response.json()
        assert response.status_code == 200
        return services_

    def get_unused_service(self, client_services, services):
        """Return a unused service"""
        assert services['items']
        for item in services['items']:
            if item not in client_services['items']:
                return item['id'], item['cost']

    def add_new_service_to_client(self, client_id, service_id):
        """Adds a new service to the client"""
        assert service_id
        url = self.url_join('client/add_service')
        data = {'client_id': client_id, 'service_id': service_id}
        response = requests.post(url, headers=_HEADERS,
                                 json=data)
        assert response.status_code == 202
        return response.status_code

    def wait_appear_new_service_for_client(self, client_id, service_id,
                                           wait_time):
        """Waiting for a new service to appear in the client list"""
        end_time = dt.datetime.now() + dt.timedelta(seconds=wait_time)
        client_services_ = {}
        while dt.datetime.now() <= end_time:
            client_services_ = self.get_client_services(client_id)
            service_ids = [item['id'] for item in client_services_['items']]
            try:
                assert service_id in service_ids
                return client_services_
            except AssertionError:
                time.sleep(_TIME_SLEEP)
        else:
            if client_services_['count'] == 0:
                message = ('The client id {} does not have services. '
                           'The client possible does not exist in database'
                           .format(client_id))
            else:
                message = 'Something went wrong'
            raise TimeoutError('Exceeded waiting time request... {message}'
                               .format(message=message))

    def get_client_balance(self, client_id):
        """Return current balance of client"""
        query_balance = self.cursor.execute('SELECT BALANCE FROM BALANCES '
                                            'WHERE CLIENTS_CLIENT_ID=?',
                                            (client_id,))
        balance, = query_balance.fetchone()
        assert balance
        return balance

    @staticmethod
    def check_balance_reduced_to_service_cost(start_balance,
                                              current_balance, service_cost):
        """Check current balance of client and calculated balance"""
        expected_balance = start_balance - service_cost
        try:
            assert current_balance == expected_balance
        except AssertionError:
            raise AssertionError('Expected balance of client to be {expected}'
                                 ' but was {current}'
                                 .format(expected=expected_balance,
                                         current=current_balance))
