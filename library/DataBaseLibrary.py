# -*- coding: utf-8 -*-

import sqlite3

from variables import DATABASE_PATH


class DataBaseLibrary:
    """The library provides work with the database"""
    def __init__(self):
        self._connect = sqlite3.connect(DATABASE_PATH)
        self._cursor = self._connect.cursor()

    def __del__(self):
        self._connect.close()
