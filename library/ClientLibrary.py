# -*- coding: utf-8 -*-

import time
from urllib.parse import urljoin
import datetime as dt
import random

import requests

from DataBaseLibrary import DataBaseLibrary

_TIME_SLEEP = 5
_HEADERS = {'Content-Type': 'application/json'}


class ClientLibrary(DataBaseLibrary):
    """Defines methods for testing API Clients"""
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    def __init__(self, host):
        super().__init__()
        self._host = host

    def create_or_get_existing_client_with_positive_balance(
            self, balance_for_new_client):
        """Return id and balance of client with positive balance or
        create new client if not exist"""
        client_balance_query = self._cursor.execute('SELECT * FROM BALANCES '
                                                    'WHERE BALANCE > 0 LIMIT 1')
        client_with_balance = client_balance_query.fetchone()
        if not client_with_balance:
            client_with_balance = self.add_client(balance_for_new_client)
        return client_with_balance

    def add_client(self, balance_for_new_client):
        """Add client into database and return client_id, balance"""
        self._cursor.execute('INSERT INTO CLIENTS (CLIENT_NAME) VALUES(?)',
                            ('Ringo',))
        id_client = self._cursor.lastrowid
        client_with_balance = (id_client, balance_for_new_client)
        self._cursor.execute('INSERT INTO BALANCES VALUES(?,?)',
                             client_with_balance)
        self._connect.commit()
        return client_with_balance

    def get_client_services(self, client_id):
        """Returns a dictionary with services of client"""
        data = {'client_id': client_id}
        url = urljoin(self._host, 'client/services')
        response = requests.post(url, headers=_HEADERS, json=data)
        assert response.status_code == 200
        client_services = response.json()
        return client_services

    def get_services(self):
        """Return the dictionary of available services"""
        url = urljoin(self._host, 'services')
        response = requests.get(url, headers=_HEADERS)
        services = response.json()
        assert response.status_code == 200
        return services

    def get_unused_service(self, client_services, services):
        """Return a unused service"""
        client_services_set = {(item['id'], item['cost'])
                            for item in client_services['items']}
        services_set = {(item['id'], item['cost'])
                        for item in services['items']}
        unused_service_set = {item for item in services_set
                           if item not in client_services_set}
        assert unused_service_set
        return random.choice(list(unused_service_set))

    def add_new_service_to_client(self, client_id, service_id):
        """Adds a new service to the client"""
        url = urljoin(self._host, 'client/add_service')
        data = {'client_id': client_id, 'service_id': service_id}
        response = requests.post(url, headers=_HEADERS,
                                 json=data)
        assert response.status_code == 202

    def wait_appear_new_service_for_client(self, client_id, service_id,
                                           wait_time):
        """Waiting for a new service to appear in the client list"""
        end_time = dt.datetime.now() + dt.timedelta(seconds=wait_time)
        client_services = {}
        while dt.datetime.now() <= end_time:
            client_services = self.get_client_services(client_id)
            service_ids = [item['id'] for item in client_services['items']]
            try:
                assert service_id in service_ids
                return
            except AssertionError:
                time.sleep(_TIME_SLEEP)
        else:
            if client_services['count'] == 0:
                message = ('The client id {} does not have services. '
                           'The client possible does not exist in database'
                           .format(client_id))
            else:
                message = 'Something went wrong'
            raise TimeoutError('Exceeded waiting time request... {message}'
                               .format(message=message))

    def get_client_balance(self, client_id):
        """Return current balance of client"""
        query_balance = self._cursor.execute('SELECT BALANCE FROM BALANCES '
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
        message = ('Expected balance of client to be {expected} '
                   'but was {current}'
                   .format(expected=expected_balance,
                           current=current_balance))
        assert current_balance == expected_balance, message
