'''
Setup Core and GUI databases
'''
__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import hashlib
import sqlite3

from os import path

GUI_DATABASE = 'database/db_files/gui.db'
DEFAULT_ADMIN_PWD = 'admin'


def setupGuiDatabase(BASE_DIR):
    '''
    Setup GUI database
    '''
    # Create file if not present
    db_connection = sqlite3.connect(path.join(BASE_DIR, GUI_DATABASE,))
    db_cursor = db_connection.cursor()

    # Create users table if not existing
    db_cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, firstname TEXT, lastname TEXT,'''\
                      '''password TEXT, changed INTEGER)''')
    db_connection.commit()

    # Insert default admin account if users table is empty
    db_cursor.execute('''SELECT count(username) FROM users''')
    if db_cursor.fetchall()[0][0] == 0:
        # No user
        db_cursor.execute('''INSERT INTO users VALUES ('admin', 'WAKe', 'ADMINISTRATOR', ?, 0)''',
                          (hashlib.sha512(DEFAULT_ADMIN_PWD).hexdigest(),))
        db_connection.commit()

    db_cursor.close()
    db_connection.close()
