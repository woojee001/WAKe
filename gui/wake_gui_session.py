'''
Custom session handler based on cherrypy RamSession
'''

__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

import hashlib
import random
import time

from cherrypy.lib.sessions import RamSession
from cherrypy import request

SESSION_DURATION = 3600


class WakeSession(RamSession):
    '''
    Custom session handler for WAKe
    '''

    def __init__(self, session_id=None, **kwargs):
        '''
        Creation of a WekeSession instance
        '''
        RamSession.__init__(self, id=session_id, **kwargs)

        self.setdefault('timed_out', True)
        self.setdefault('expiration_time', None)
        self.setdefault('control_token', None)
        return

    def generate_id(self):
        '''
        Generate session ID and set control token and expiration time
        '''
        if not 'User-Agent' in request.headers:
            request.headers['User-Agent'] = 'None'

        session_id = hashlib.sha512('{0:s}{1:s}{2:s}'.format(str(time.time() + random.randint(1, 1000000000)),
                                                             request.headers['User-Agent'],
                                                             request.remote.ip)).hexdigest()

        control_token = hashlib.sha512('{0:s}{1:s}'.format(request.headers['User-Agent'],
                                                           request.remote.ip)).hexdigest()

        self.update({'control_token': control_token, 'timed_out': False,
                     'expiration_time': time.time() + SESSION_DURATION})

        return session_id.upper()

    def getSessionStatus(self):
        '''
        Check session status and return it to wake GUI
        '''
        status = {'valid': False, 'authenticated': False}

        # 1) Check if session timed out
        if self.get('timed_out'):
            status['reason'] = 'timed_out'
            return status

        # 2) Check if session expired
        if time.time() >= self.get('expiration_time'):
            status['reason'] = 'expired'
            return status

        # 3) Check if session is hijacked
        if not 'User-Agent' in request.headers:
            request.headers['User-Agent'] = 'None'

        control_token = hashlib.sha512('{0:s}{1:s}'.format(request.headers['User-Agent'],
                                                           request.remote.ip)).hexdigest()

        if control_token != self.get('control_token'):
            status['reason'] = 'hijacked'
            return status

        # Session is valid
        status['valid'] = True

        # 4) Check if user is authenticated
        if self.get('authenticated', False):
            status['authenticated'] = True

        return status
