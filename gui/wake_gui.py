'''
    Web Application Keeper (WAKe) GUI
    Powers a GUI for administration and configuration purpose
'''
__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import cherrypy
import hashlib
import json
import multiprocessing

from os.path import join

from database.setup_db import setupGuiDatabase
from database.db_connector import GuiDatabaseConnector

def handleUnexpectedError():
    '''
        Custom error handler, do not display error message
    '''
    cherrypy.response.status = 302
    cherrypy.response.headers['Location'] = '/'
    return

def handleExpectedError(status, message, traceback, version):
    '''
        Custom HTTP error handler, do not display error message
    '''
    cherrypy.response.status = 302
    cherrypy.response.headers['Location'] = '/'
    return

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
        if not self._DEBUG: #If not in debug mode, activate custom error handlers
            self._cp_config =   {
                                    'request.error_response': handleUnexpectedError,
                                    'error_page.default': handleExpectedError
                                }
        self._db_connector = db_connector
        return
    
    @cherrypy.expose
    def index(self):
        try:
            html = ''.join(open(join(self._BASE_DIR, 'login.html'), 'r').readlines())
        except:
            html = ''
        return html
    
    @cherrypy.expose
    def getPageHeader(self):
        '''
            Return HTML content for the page "Header" zone
        '''
        try:
            html = u''.join(open(join(self._BASE_DIR, 'resources', 'html', 'unauthenticated_header.html')).readlines())
        except:
            html = 'NO HEADER'
        return '{"success": true, "html": %s}' %(json.dumps(html),)
    
    @cherrypy.expose
    def connect(self, username='', password=''):
        '''
            Authenticate user
        '''
        connected = self._db_connector.execute(request='''SELECT changed FROM users WHERE username=? AND password=?''',
                                               attributes=(username, hashlib.sha512(password).hexdigest(),)
                                               )
        if connected:
            return '{"success": true}'
        return '{"success": false}'

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
        #Setup GUI database and connector
        setupGuiDatabase(self._PROJECT_DIR)
        db_connector = GuiDatabaseConnector(self._PROJECT_DIR)
        
        #Setup web app. configuration
        appconf = { 
            '/': {'tools.staticdir.root': self._BASE_DIR},
            '/app': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'app'},
            '/extjs': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'extjs'},
            '/resources': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'resources'},
            '/favicon.ico': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'favicon.ico')},
            '/login.js': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'login.js')},
        }
        
        siteconf = {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': self._PORT,
            'log.screen': False,
            'engine.autoreload.on': False
        }
        
        #Upload configuration
        cherrypy.config.update(siteconf)
        
        #Use HTTPS
        cherrypy.server.ssl_certificate = './gui/conf/ssl/server.crt'
        cherrypy.server.ssl_private_key = './gui/conf/ssl/server.key'
        
        #Create server and application
        cherrypy.tree.mount(WakeGuiApp(self._BASE_DIR, self._DEBUG, db_connector), '/', appconf)
        
        #Start CherryPy server
        cherrypy.server.start() 
        cherrypy.engine.start()
        cherrypy.engine.block()
