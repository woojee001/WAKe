'''
Core and GUI database connectors
'''
__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import sqlite3

from os import path

from setup_db import GUI_DATABASE


class GuiDatabaseConnector():
    '''
    Interface with GUI DB
    '''
    def __init__(self, PROJEC_DIR):
        '''
        Setup connector
        '''
        self._FILE = path.join(PROJEC_DIR, GUI_DATABASE)
        return

    def execute(self, request='', attributes=()):
        '''
        sPerform request
        '''
        db_connection = sqlite3.connect(self._FILE)
        db_cursor = db_connection.cursor()

        # Execute instruction
        db_cursor.execute(request, attributes)
        db_connection.commit()

        # Get result
        result = db_cursor.fetchall()

        db_cursor.close()
        db_connection.close()

        return result
