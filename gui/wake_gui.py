'''
Web Application Keeper (WAKe) GUI
Powers up a GUI for administration and configuration purpose
'''
from cherrypy._cperror import HTTPRedirect
__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import cherrypy
import hashlib
import json
import multiprocessing
import random
import threading
import time

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
        if not self._DEBUG:  # If not in debug mode, activate custom error handlers
            self._cp_config =   {
                                    'request.error_response': handleUnexpectedError,
                                    'error_page.default': handleExpectedError
                                }
        self._db_connector = db_connector
        self._user_sessions = {}
        self._user_sessions_lock = threading.Lock()
        self._SESSION_DURATION = 3600
        self._UNAUTH_SESSION_DURATION = 600
        return
    
    def _getSessionCookie(self, request):
        '''
        Return the WAKe_SESSION_ID
        '''
        try:
            return request.cookie['WAKe_SESSION_ID']
        except:
            return None
    
    def _generateSessionId(self, request):
        '''
        Set WAKe_SESSION_ID value + control
        '''
        value = hashlib.md5('{0:s}{1:s}{2:s}'.format(str(time.time() + random.randint(1, 1000000000)),
                                                     request.headers['User-Agent'],
                                                     request.remote.ip)).hexdigest()
        control = hashlib.md5('{0:s}{1:s}'.format(request.headers['User-Agent'],
                                                  request.remote.ip)).hexdigest()
        
        # Memorize session
        self._user_sessions_lock.acquire()
        self._user_sessions[value] = {
                                        'control_token': control,
                                        'expiration_time': -1,
                                        'username': None,
                                        'creation_time': time.time(),
                                        'website_id': None
                                      }
        self._user_sessions_lock.release()
        
        return '{0:s}{1:s}'.format(value, control,)
    
    def _setSessionCookie(self, request):
        '''
        Set WAKe_SESSION_ID
        '''
        cookie_list = cherrypy.response.cookie
        cookie_list['WAKe_SESSION_ID'] = self._generateSessionId(request)
        return cookie_list['WAKe_SESSION_ID']
    
    def _checkSessionId(self, cookie, request, no_standard_checks=False, check_duplicate=False, static_username='', set_duplicate=False):
        '''
        Check status of the specified session ID
        '''
        status = {
                    'exists': True,
                    'expired': False,
                    'duplicate': False,
                    'hijacked': False,
                    'authenticated': False
                  }
        
        if not no_standard_checks:
            
            # Check if session exists
            if not cookie.value[0:32] in self._user_sessions:
                status['exists'] = False
                return status
            
            # Check if session expired
            if 'expiration_time' in self._user_sessions[cookie.value[0:32]]:
                if time.time() > self._user_sessions[cookie.value[0:32]]['expiration_time'] + self._SESSION_DURATION and \
                        self._user_sessions[cookie.value[0:32]]['expiration_time'] > 0:
                    self._user_sessions_lock.acquire()
                    del self._user_sessions[cookie.value[0:32]]
                    self._user_sessions_lock.release()
                    status['expired'] = True
                    return status
                
            # Clean sessions list
            sessions_to_del = []
            self._user_sessions_lock.acquire()
            for session_id in self._user_sessions:
                if 'expiration_time' in self._user_sessions[session_id] and self._user_sessions[session_id]['expiration_time'] > 0:
                    if time.time() > self._user_sessions[session_id]['expiration_time'] + self._SESSION_DURATION:
                        sessions_to_del.append(session_id)
                elif time.time() > self._user_sessions[session_id]['creation_time'] + self._UNAUTH_SESSION_DURATION:
                    sessions_to_del.append(session_id)
            for session_id in sessions_to_del:
                del self._user_sessions[session_id]
            self._user_sessions_lock.release()
            
            # Check if cookie was tampered/hijacked
            if cookie.value[32:] != self._user_sessions[cookie.value[0:32]]['control_token']:
                status['hijacked'] = True
                self._user_sessions_lock.acquire()
                del self._user_sessions[cookie.value[0:32]]  # Remove tampered/hijacked session
                self._user_sessions_lock.release()
                return status

        # Check if session is duplicated and if user is authenticated
        if check_duplicate:
            # Specific check for "connect" action
            self._user_sessions_lock.acquire()
            for session_id in self._user_sessions:
                if session_id != cookie.value[0:32]:
                    if static_username == self._user_sessions[session_id]['username']:
                        # Check if a session already exists with a specific username
                        status['duplicate'] = True
                        if set_duplicate:
                            self._user_sessions[session_id]['duplicate'] = 1
                        self._user_sessions_lock.release()
                        return status
            self._user_sessions_lock.release()
            
        elif self._user_sessions[cookie.value[0:32]]['username']:
            # Standard check if username exists
            self._user_sessions_lock.acquire()
            if 'duplicate' in self._user_sessions[cookie.value[0:32]]:
                status['duplicate'] = True
                self._user_sessions_lock.release()
                return status
            self._user_sessions_lock.release()
            if self._user_sessions[cookie.value[0:32]]['username']:
                status['authenticated'] = True
        
        return status
    
    def _checkSession(self, request, no_standard_checks=False, check_duplicate=False, static_username='', set_duplicate=False):
        '''
        Check if we can proceed or not
        '''
        # Get session cookie
        cookie = self._getSessionCookie(request)
        if not cookie:
            return None, None
        
        # Check session status
        session_status = self._checkSessionId(cookie, request, no_standard_checks=no_standard_checks,
                                              check_duplicate=check_duplicate, 
                                              static_username=static_username, set_duplicate=set_duplicate)
        
        return cookie.value[0:32], session_status
    
    @cherrypy.expose
    def index(self):
        '''
        WAKe root page
        '''
        # Get session cookie
        cookie = self._getSessionCookie(cherrypy.request)
        if not cookie:
            # Set session ID
            cookie = self._setSessionCookie(cherrypy.request)
        wake_session_id = cookie.value[0:32]
        
        # Check session status
        session_status = self._checkSessionId(cookie, cherrypy.request)
        if not session_status['exists']:
            # Set session ID
            self._setSessionCookie(cherrypy.request)
        
        # Check if session ID was hijacked
        if session_status['hijacked']:
            file_to_load = join(self._BASE_DIR, 'login_hijacked.html')
            
        # Check if duplicate session
        elif session_status['duplicate']:
            file_to_load = join(self._BASE_DIR, 'login_duplicate.html')
            self._user_sessions_lock.acquire()
            del self._user_sessions[wake_session_id]
            self._user_sessions_lock.release()
                
        # Check if user is authenticated
        elif session_status['authenticated']:
            # Check if default pwd was changed and then web site configuration was selected
            if not self._user_sessions[wake_session_id]['pwd_changed']:
                file_to_load = join(self._BASE_DIR, 'change_pwd.html')
            elif not self._user_sessions[wake_session_id]['website_id']:
                file_to_load = join(self._BASE_DIR, 'select.html')
            else:    
                file_to_load = join(self._BASE_DIR, 'wake.html')
        
        # Unauthenticated user
        else:
            file_to_load = join(self._BASE_DIR, 'login.html')
        
        # Display selected page
        try:
            html = ''.join(open(file_to_load, 'r').readlines())
        except:
            html = 'ERROR LOADING PAGE CONTENT'
        return html
    
    @cherrypy.expose
    def getPageHeader(self):
        '''
        Return HTML content for the page "Header" zone
        '''
        # Get session status & session cookie
        wake_session_id, session_status = self._checkSession(cherrypy.request)
        
        # Check what header we have to return
        if session_status['authenticated']:
            try:
                html = u''.join(open(join(self._BASE_DIR, 'resources', 'html', 'authenticated_header.html')).readlines())
            except:
                html = 'NO HEADER'
            return '{{"success": true, "html": {0:s}}}'.format(json.dumps(html.replace('~~USERNAME~~',
                                                                                       self._user_sessions[wake_session_id]['username'])))
        
        try:
            html = u''.join(open(join(self._BASE_DIR, 'resources', 'html', 'unauthenticated_header.html')).readlines())
        except:
            html = 'NO HEADER'
        return '{{"success": true, "html": {0:s}}}'.format(json.dumps(html))
    
    @cherrypy.expose
    def connect(self, username='', password=''):
        '''
        Authenticate user
        '''
        # Get session status & session cookie
        wake_session_id, session_status = self._checkSession(cherrypy.request)
        
        # Check status
        if session_status['hijacked'] or not session_status['exists']:
            return '{"success": false}'
        
        connected = self._db_connector.execute(request='''SELECT changed FROM users WHERE username=? AND password=?''',
                                               attributes=(username, hashlib.sha512(password).hexdigest(),))
        # Return connect result
        if connected:
            # Re-check session status (for duplicate)
            wake_session_id, session_status = self._checkSession(cherrypy.request, no_standard_checks=True,
                                                                 check_duplicate=True, static_username=username)
            
            self._user_sessions[wake_session_id]['pwd_changed'] = connected[0][0]  # Get info about default pwd change
            
            if session_status['duplicate']:
                self._user_sessions_lock.acquire()
                self._user_sessions[wake_session_id]['duplicate_username'] = username
                self._user_sessions_lock.release()
                return '{"success": true, "duplicate": true, "msg": "An older session with the username you specified already exists. Do you wish to overwritte it ?"}'
            
            self._user_sessions[wake_session_id]['expiration_time'] = time.time() + self._SESSION_DURATION
            self._user_sessions_lock.acquire()
            self._user_sessions[wake_session_id]['username'] = username
            self._user_sessions_lock.release()
            return '{"success": true, "duplicate": false}'
        
        return '{"success": false, "duplicate": false, "msg": "Wrong username or password"}'
    
    @cherrypy.expose
    def confirmDuplicate(self, _dc=None):
        '''
        Confirm overwrite of a duplicate session
        '''
        # Get session status & session cookie
        wake_session_id, session_status = self._checkSession(cherrypy.request)
        
        # Check status
        if session_status['duplicate'] or session_status['hijacked'] or not session_status['exists']:
            return '{"success": true}'
        
        # Set duplicate
        _, _ = self._checkSession(cherrypy.request, no_standard_checks=True, check_duplicate=True, 
                                  static_username=self._user_sessions[wake_session_id]['duplicate_username'],
                                  set_duplicate=True)
        
        self._user_sessions_lock.acquire()
        self._user_sessions[wake_session_id]['username'] = self._user_sessions[wake_session_id]['duplicate_username']
        self._user_sessions[wake_session_id]['expiration_time'] = time.time() + self._SESSION_DURATION
        del self._user_sessions[wake_session_id]['duplicate_username']
        self._user_sessions_lock.release()
        
        return '{"success": true}'
    
    @cherrypy.expose
    def logout(self):
        '''
        Destroy active session
        '''
        # Get session status & session cookie
        wake_session_id, _ = self._checkSession(cherrypy.request)
        
        #Destroy session
        try:
            del self._user_sessions[wake_session_id]
        except:
            pass
        
        raise HTTPRedirect('/', 302)
        
    
    @cherrypy.expose
    def changeDefaultPassword(self, password1, password2):
        '''
        Change default password for admin account
        '''
        # Get session status & session cookie
        wake_session_id, session_status = self._checkSession(cherrypy.request)
        
        # Check status
        if session_status['duplicate'] or session_status['hijacked'] or not session_status['exists']:
            return '{"success": true, "duplicate": true}'
        
        # Check if value was submitted and if both match
        if not password1 or password1 != password2:
            return '{"success": false, "duplicate": false, "msg": "The specified values do not match"}'
        
        # Change password
        self._user_sessions[wake_session_id]['pwd_changed'] = 1
        _ = self._db_connector.execute(request='''UPDATE users SET changed=1, password=? WHERE username=?''',
                                       attributes=(hashlib.sha512(password1).hexdigest(),
                                                   self._user_sessions[wake_session_id]['username'],))
        
        return '{"success": true}'
            
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
            '/app': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'app'},
            '/extjs': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'extjs'},
            '/resources': {'tools.staticdir.on': True, 'tools.staticdir.dir': 'resources'},
            '/favicon.ico': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'favicon.ico')},
            '/login.js': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'login.js')},
            '/change_pwd.js': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'change_pwd.js')},
            '/select.js': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'select.js')},
            '/wake.js': {'tools.staticfile.on': True, 'tools.staticfile.filename': join(self._BASE_DIR, 'wake.js')},
        }
        
        siteconf = {
            'server.socket_host': '0.0.0.0',
            'server.socket_port': self._PORT,
            'log.screen': False,
            'engine.autoreload.on': False
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
