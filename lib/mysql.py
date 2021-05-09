import mysql.connector
from configparser import ConfigParser
import os
import sys

CONFG_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '../config')


class DB:

    def __init__(self):
        try:
            self.config = ConfigParser()
            self.config.read(os.path.join(
                CONFG_DIR, self.__class__.__name__ + '.ini'))

            self.connection = mysql.connector.connect(
                host=self.config['mysql']['host'],
                user=self.config['mysql']['user'],
                password=self.config['mysql']['password'],
                port=self.config['mysql']['port'],
                database=self.config['mysql']['db']
            )
            if self.connection:
                self.cursor = self.connection.cursor()
        except Exception as e:
            print('error on line no {0} {1}'.format(
                sys.exc_info()[-1].tb_lineno, e))
            self.cursor.close()

    def query_database_many(self, query, params=None):
        try:
            if params:
                result = self.cursor.executemany(query, params)
            if result:
                return result
            self.connection.commit()
            print('inserted successfully')
            self.cursor.close()
        except Exception as e:
            print('error on line no {0} {1}'.format(
                sys.exc_info()[-1].tb_lineno, e))
            self.cursor.close()

    def query_database_one(self, query, params=None):
        try:
            if params:
                result = self.cursor.execute(query, params)
            result = self.cursor.execute(query)
            if result:
                return result
            self.connection.commit()
            print('inserted successfully')
            self.cursor.close()
        except Exception as e:
            print('error on line no {0} {1}'.format(
                sys.exc_info()[-1].tb_lineno, e))
            self.cursor.close()
