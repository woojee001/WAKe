'''
Web Application Keeper (WAKe) GUI
Powers up a GUI for administration and configuration purpose
'''

__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import cherrypy
import multiprocessing

from os.path import join

import wake_gui_session as wake

from database.setup_db import setupGuiDatabase
from database.db_connector import GuiDatabaseConnector
from lib.pyratemp import pyratemp

cherrypy.lib.sessions.WakeSession = wake.WakeSession


class WakeGuiApp():
    '''
    Class that defines the structure of the UI application and the underlying operations
    '''
    def __init__(self, BASE_DIR, DEBUG, db_connector):
        '''
        Configure application
        '''
        self._BASE_DIR = BASE_DIR
        self._DEBUG = DEBUG
        if not self._DEBUG:  # If not in debug mode, activate custom error handlers
            self._cp_config = {
                                    # 'request.error_response': handleUnexpectedError,
                                    # 'error_page.default': handleExpectedError
                                }
        self._db_connector = db_connector
        return

    @cherrypy.expose
    def index(self):
        '''
        WAKe root page
        '''
        # Initialize local variables
        messages = []

        # Get session status
        session_status = cherrypy.session.getSessionStatus()
        print session_status

        # Check if session is valid
        if not session_status['valid']:

            # Store what append
            messages.append(session_status['reason'])

            # Generate new session
            cherrypy.session.delete()
            cherrypy.session.regenerate()

        # Set what file to open
        if not session_status['authenticated']:
            file_to_load = join(self._BASE_DIR, 'login.html')
        else:
            file_to_load = join(self._BASE_DIR, 'index.html')

        # Display selected page
        try:
            html_template = pyratemp.Template(filename=file_to_load)
            html = html_template(messages_meta=messages)
        except:
            html = 'ERROR LOADING PAGE CONTENT'
        return html


class WakeGui(multiprocessing.Process):
    '''
    UI starter
    '''
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        '''
        Set needed variables
        '''
        multiprocessing.Process.__init__(self, group=group, target=target, name=name)
        self._PROJECT_DIR = args[0]
        self._BASE_DIR = join(self._PROJECT_DIR, 'gui', 'www')
        self._PORT = args[1]
        self._DEBUG = args[2]
        return

    def run(self):
        '''
        Create, configure and start UI web server & application
        '''
        # Setup GUI database and connector
        setupGuiDatabase(self._PROJECT_DIR)
        db_connector = GuiDatabaseConnector(self._PROJECT_DIR)

        # Setup web app. configuration
        appconf = {
            '/': {'tools.staticdir.root': self._BASE_DIR},
            '/app': {'tools.staticdir.on': True,
                     'tools.staticdir.dir': 'app'},
            '/extjs': {'tools.staticdir.on': True,
                       'tools.staticdir.dir': 'extjs'},
            '/resources': {'tools.staticdir.on': True,
                           'tools.staticdir.dir': 'resources'},
            '/favicon.ico': {'tools.staticfile.on': True,
                             'tools.staticfile.filename': join(self._BASE_DIR, 'favicon.ico')},
            '/login.js': {'tools.staticfile.on': True,
                          'tools.staticfile.filename': join(self._BASE_DIR, 'login.js')},
        }

        siteconf = {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': self._PORT,
            'log.screen': False,
            'engine.autoreload.on': False,
            'tools.sessions.on': True,
            'tools.sessions.storage_type': 'wake',
            'tools.sessions.name': 'WAKe_SESSION_ID',
            'tools.sessions.timeout': 0.5,
            'tools.sessions.persistent': False
        }

        # Upload configuration
        cherrypy.config.update(siteconf)

        # Use HTTPS
        cherrypy.server.ssl_certificate = './gui/conf/ssl/server.crt'
        cherrypy.server.ssl_private_key = './gui/conf/ssl/server.key'

        # Create server and application
        cherrypy.tree.mount(WakeGuiApp(self._BASE_DIR, self._DEBUG, db_connector), '/', appconf)

        # Start CherryPy server
        cherrypy.server.start()
        cherrypy.engine.start()
        cherrypy.engine.block()
