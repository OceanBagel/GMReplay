# Built-in packages
import sys
from os import chdir, system
from traceback import format_exc

# Constants
import constants as c

# Local packages
from ui import mainWindowClass


def main():
    # Init
    print(c.STARTUP_STRING)  # "GMReplay " + VERSION_NUMBER + " by OceanBagel\n"

    # Change the working directory to the temp directory (only for the release version, distributed as a packed exe)
    if hasattr(sys, "_MEIPASS"):
        chdir(sys._MEIPASS)

    # Enforce a minimum Python version
    if sys.version_info < c.MIN_PYTHON:
        print(c.MIN_PYTHON_STRING)
        return

    # Initialize tkinter window
    mainWindowObj = mainWindowClass()

    # Execute main loop, broken apart to process stdout from the game window
    while mainWindowObj.windowExists:
        mainWindowObj.root.update_idletasks()
        mainWindowObj.root.update()

        # Prevent blocking from the game process and print game's stdout to the console
        if mainWindowObj.gameProcess is not None:
            if mainWindowObj.config.General.suppress_game_debug_output == "False":
                for line in mainWindowObj.gameProcess.stdout:
                    print(line.decode("utf-8").strip())

            # If it is not none, the game was closed
            if mainWindowObj.gameProcess.poll() is not None:
                print(c.GAME_CLOSED_STRING)
                # Clear the variable until it's used again
                mainWindowObj.gameProcess = None
                # Enable buttons
                mainWindowObj.recordPlayRow.movieEnd()


if __name__ == "__main__":
    try:
        main()
    # If there was an exception, leave the console open and await user input as a graceful exit
    except Exception:
        # Print the exception
        print(format_exc())
    finally:
        # Skip the pause if debugging
        if "debugpy" in sys.modules:
            print("Debugger detected. Skipping pause command and exiting.")

        else:
            system("pause")
