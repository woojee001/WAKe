'''
Web Application Keeper (WAKe)
Blacklist/whitelist Web Application Firewall (WAF)
'''

__author__ = 'Aurelien CROZATIER'
__version__ = 0.1

from argparse import ArgumentParser
from os import mkdir
from os.path import dirname, abspath, join
from sys import argv
from threading import Event

from gui.wake_gui import WakeGui


def parseArgs(arguments):
    '''
    Define available command line arguments
    '''
    parser = ArgumentParser(prog='WAKe',
                            description='Blacklist/whitelist Web Application Firewall (WAF)')

    parser.add_argument('-d', '--debug', action='store_true',
                        help='Activate debug mode (relevant only for development)')

    parser.add_argument('--no-core', action='store_true', dest='no_core',
                        help='Do not start the WAKe core (offline configuration)')

    parser.add_argument('--no-gui', action='store_true', dest='no_gui',
                        help='Do not start the GUI')

    parser.add_argument('-p', '--port', type=int, dest='ui_port', action='store', default=3333,
                        help='TCP port on which the GUI will be available (default: 3333')

    return parser.parse_args(arguments)

if __name__ == '__main__':

    # Parse command line arguments
    arguments = parseArgs(argv[1:])  # Ignore script name

    # Get the path of the project directory
    PROJECT_DIR = dirname(abspath(__file__))

    # Create database files directory
    try:
        mkdir(join(PROJECT_DIR, 'database', 'db_files'))
    except:
        pass  # Repository exists

    # Start GUI
    if not arguments.no_gui:
        wake_gui = WakeGui(args=(PROJECT_DIR, arguments.ui_port, arguments.debug,))
        wake_gui.start()

    # Start proxy core
    if not arguments.no_core:
        pass

    # Run WAKe
    stop_running = Event()
    try:
        while not stop_running.isSet():
            if not arguments.no_gui:
                # Check if UI thread exited
                if not wake_gui.is_alive():
                    stop_running.set()

            if not arguments.no_core:
                # Check if core thread exited
                pass

            stop_running.wait(10)

    except KeyboardInterrupt:
        if not arguments.no_gui:
            # Stop UI
            wake_gui.terminate()

        if not arguments.no_core:
            # Stop core
            pass
