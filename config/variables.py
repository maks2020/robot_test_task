import os

HOST = 'http://localhost'
PORT = 5000
WAIT_TIME = 60
BALANCE_FOR_NEW_CLIENT = 5.0
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATABASE_PATH = os.path.join(BASE_DIR, 'aut/web', 'clients.db')