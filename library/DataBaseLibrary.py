# -*- coding: utf-8 -*-

import sqlite3


class DataBaseLibrary:
    """The library provides work with the database"""
    def __init__(self):
        self._connect = None
        self._cursor = None

    def connect_to_db(self, db_path):
        """Connect to database"""
        self._connect = sqlite3.connect(db_path)
        self._cursor = self._connect.cursor()

    def close_db(self):
        """Close connection with database"""
        self._connect.close()
        self._cursor = None
        self._connect = None
