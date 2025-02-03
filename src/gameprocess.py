# Built-in packages
import subprocess
from os import getcwd, set_blocking

from asyncssh import STDOUT
from psutil import Process

# Constants
import constants as c

# Local packages
from patching import genPatchedExe


def recordOrPlayMovie(mainWindowObj, selection):
    ## Handles recording (selection is 1 aka RECORD) or playback (selection is 2 aka PLAY)

    # Attempt to patch the exe file
    pathToExe = genPatchedExe(mainWindowObj.exeFileRow.combobox.get())

    # Save the movie if it's in playback mode
    if selection == c.PLAY:
        mainWindowObj.saveMovieInputs()

    # Run the game with the record command
    print(c.GAME_START_STRING)

    myargs = [
        pathToExe,
        ("-record" if selection == c.RECORD else "-playback"),
        mainWindowObj.movieFileRow.combobox.get(),
        "-game",
        mainWindowObj.dataWinFileRow.combobox.get(),
        "-sleepmargin",
        "0",
    ]

    # This one hides the console output
    if mainWindowObj.config.General.suppress_game_debug_output == "True":
        mystdout = subprocess.DEVNULL

    # This one shows the console output
    else:
        myargs += [
            "-debugoutput",
            getcwd() + "\\debugoutput.log",
            "|",
            "cat",
        ]
        mystdout = subprocess.PIPE

    mainWindowObj.gameProcess = subprocess.Popen(args=myargs, stdout=mystdout, stderr=STDOUT)

    if mainWindowObj.config.General.suppress_game_debug_output != "True":
        # Prevent blocking of the game process
        set_blocking(mainWindowObj.gameProcess.stdout.fileno(), False)


def getMainThreadID(gameProcess):
    ## Returns the game's GUI thread ID given the game process id from subprocess
    
    # First retrieve the process ID
    pid = gameProcess.pid
    
    # Now search for the correct thread ID. The main thread is the oldest which is first in the list.
    tid = Process(pid).threads()[0].id

    return tid