# -*- coding: utf-8 -*-

import sqlite3


class DataBaseLibrary:
    """The library provides work with the database"""
    def __init__(self, database_path):
        self.database_path = database_path
        self.connect = sqlite3.connect(self.database_path)
        self.cursor = self.connect.cursor()

    def __del__(self):
        self.connect.close()
