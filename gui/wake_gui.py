'''
    Web Application Keeper (WAKe) GUI
    Powers a GUI for administration and configuration purpose
'''

__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import cherrypy
import json
import multiprocessing

from os.path import join

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
    def __init__(self, BASE_DIR, DEBUG):
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

class WakeGui(multiprocessing.Process):
    '''
        UI starter
    '''
    def __init__(self, group=None, target=None, name=None, args=(), kwargs=None, verbose=None):
        '''
            Set needed variables
        '''
        multiprocessing.Process.__init__(self, group=group, target=target, name=name)
        self._BASE_DIR = join(args[0], 'gui', 'www')
        self._PORT = args[1]
        self._DEBUG = args[2]
        return
    
    def run(self):
        '''
            Create, configure and start UI web server & application
        '''
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
        
        #Create server and application
        cherrypy.tree.mount(WakeGuiApp(self._BASE_DIR, self._DEBUG), '/', appconf)
        
        #Start CherryPy server
        cherrypy.server.start() 
        cherrypy.engine.start()
        cherrypy.engine.block()
