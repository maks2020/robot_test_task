import random
import time
from urllib.parse import urljoin
from datetime import datetime
import sqlite3

import requests

_TIME_SLEEP = 5


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
    _HEADERS = {'Content-Type': 'application/json'}

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

    def get_client_services(self, client_balance):
        """Return the dictionary services of client"""
        client_id, _ = client_balance
        data = {'client_id': client_id}
        url = self.url_join('client/services')
        response = requests.post(url, headers=ClientLibrary._HEADERS, json=data)
        assert response.status_code == 200
        client_services_ = response.json()
        return client_services_

    def get_services(self):
        """Return the dictionary of available services"""
        url = self.url_join('services')
        response = requests.get(url, headers=ClientLibrary._HEADERS)
        services_ = response.json()
        assert response.status_code == 200
        return services_

    def get_unused_services(self, client_services, services):
        """Return a random unused service"""
        if client_services['count'] != services['count']:
            diff_services = [item for item in services['items']
                             if item not in client_services['items']]
            unused_service = random.choice(diff_services)
            assert unused_service
            return unused_service

    def set_client_service(self, client_balance, unused_service):
        """Set a service for client"""
        id_client, _ = client_balance
        id_service = unused_service['id']
        if id_service:
            url = self.url_join('client/add_service')
            data = {'client_id': id_client, 'service_id': id_service}
            response = requests.post(url, headers=ClientLibrary._HEADERS,
                                     json=data)
            assert response.status_code == 202
            return response.status_code

    def wait_new_service(self, client_balance, unused_service, wait_time):
        """Waiting for a new service to appear in the client list"""
        id_client, _ = client_balance
        id_service = unused_service['id']
        start_time = datetime.now()
        while True:
            client_services_ = self.get_client_services(client_balance)
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
            time.sleep(_TIME_SLEEP)

    def get_client_balances(self, client_balance, unused_service):
        """Return current and estimated balances of client"""
        id_client, start_balance = client_balance
        cost_service = unused_service['cost']
        query_balance = self.cursor.execute('SELECT BALANCE FROM BALANCES '
                                            'WHERE CLIENTS_CLIENT_ID=?',
                                            (id_client,))
        current_balance, = query_balance.fetchone()
        assert current_balance
        end_balance = start_balance - cost_service
        return current_balance, end_balance

