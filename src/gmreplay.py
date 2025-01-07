# Outside packages
import sys
from traceback import format_exc
from os import system, chdir

# Local packages
from ui import mainWindowClass

# Constants
import constants as c


def main():
    # Init
    print(c.STARTUP_STRING) # "GMReplay " + VERSION_NUMBER + " by OceanBagel\n"

    # Change the working directory to the temp directory (only applies to the release version, distributed as a packed exe)
    try:
        chdir(sys._MEIPASS)
    except AttributeError: # If this doesn't exist, we're not running the release and so we can continue
        pass

    # Enforce a minimum Python version
    if sys.version_info < c.MIN_PYTHON:
        print(c.MIN_PYTHON_STRING) # "Python %s.%s or later is required.\n" % MIN_PYTHON
        return

    # Initialize tkinter window
    mainWindowObj = mainWindowClass()

    # Execute main loop, broken apart to process stdout from the game window
    while mainWindowObj.windowExists:
        mainWindowObj.root.update_idletasks()
        mainWindowObj.root.update()

        # Prevent blocking from the game process and print game's stdout to the console
        if mainWindowObj.gameProcess != None:
            if mainWindowObj.config.General.suppress_game_debug_output == "False":
                for line in mainWindowObj.gameProcess.stdout:
                    print(line.decode('utf-8').strip())

            if mainWindowObj.gameProcess.poll() != None: # If it is not none, the game was closed
                print(c.GAME_CLOSED_STRING)
                mainWindowObj.gameProcess = None # Clear the variable until it's used again
                mainWindowObj.recordPlayRow.movieEnd() # Enable buttons


if __name__ == '__main__':
    try:
        main()
    except: # If there was an exception, leave the console open and await user input
        print(format_exc())
    finally:
        system("pause")
