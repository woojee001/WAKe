'''
Custom session handler based on cherrypy RamSession
'''

__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

from cherrypy.lib.sessions import RamSession


class WakeSession(RamSession):
    '''
    Custom session handler for WAKe
    '''

    def __init__(self, session_id=None, **kwargs):
        '''
        Creation of a WekeSession instance
        '''
        RamSession.__init__(self, id=session_id, **kwargs)
        return
