'''
    Web Application Keeper (WAKe)
    Python blacklist/whitelist Web Application Firewall (WAF) 
'''

__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

from argparse import ArgumentParser
from os.path import dirname, abspath
from sys import argv
from time import sleep

from gui.wake_gui import WakeGui

def parseArgs(arguments):
    '''
        Define available command line arguments
    '''
    parser = ArgumentParser(prog='WAKe', description='Python blacklist/whitelist Web Application Firewall (WAF)')
    
    parser.add_argument('-d', '--debug', action='store_true', help='Activate debug mode (relevant only for development)')
    parser.add_argument('--no-core', action='store_true', dest='no_core', help='Do not start the WAKe core (offline configuration)')
    parser.add_argument('--no-gui', action='store_true', dest='no_gui', help='Do not start the GUI')
    parser.add_argument('-p', '--port', type=int, dest='ui_port', action='store', default=8080, help='TCP port on which the GUI will be available (default: 6666')
    
    return parser.parse_args(arguments)

if __name__ == '__main__':
    
    #Parse command line arguments
    arguments = parseArgs(argv[1:]) #Ignore script name
    
    #Get the path of the project directory
    PROJECT_DIR = dirname(abspath(__file__))
    
    #Start GUI
    if not arguments.no_gui:
        wake_gui = WakeGui(args=(PROJECT_DIR, arguments.ui_port, arguments.debug,))
        wake_gui.start()
    
    #Start proxy core
    if not arguments.no_core:
        pass
    
    #Run WAKe
    running = True
    try:
        while running:
            if not arguments.no_gui:
                #Check if UI thread exited
                wake_gui.join(1)
                if not wake_gui.is_alive():
                    running = False
                    
            if not arguments.no_core:
                #Check if core thread exited
                pass
            
            sleep(10) #Ctrl+C does not "break" the join wait
    except KeyboardInterrupt:
        if not arguments.no_gui:
            #Stop UI
            wake_gui.terminate()
        
        if not arguments.no_core:
            #Stop core
            pass