import logging
import json

import mysql.connector
from mysql.connector import Error

config = json.load(open(".config.json"))

class DatabaseManager:
    def __init__(self):   
        self.connection = None
        self.cursor = None

    def connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=config["database"]["host"],
                user=config["database"]["user"],
                passwd=config["database"]["passwd"],
                database=config["database"]["database"]
            )
            self.cursor = self.connection.cursor(dictionary=True, buffered=True)
        except Error as err:
            self.connection, self.cursor = None, None

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
    
    def commit(self):
        self.connection.commit()

