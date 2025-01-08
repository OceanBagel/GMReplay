# Built-in packages
import subprocess
from itertools import compress
from os import getcwd, path, set_blocking
from tkinter import IntVar, Label, Menu, PhotoImage, StringVar, Tk, Toplevel, filedialog, ttk

# Outside packages
from tksheet import Sheet

# Constants
import constants as c

# Local packages
from config import configLoad, configSave
from movieparsing import inputsToRecording, loadMovie, recordingToInputs, saveMovie
from patching import genPatchedExe
from utils import folder, keyCodes, keyName, openURL, reduceBitwiseOr, rotate2DArray, stringify


class mainWindowClass:
    """
    A class to hold properties and methods in the main window
    """

    def __init__(self):
        # Load the configuration
        self.config = configLoad(c.CONFIG_PATH)

        # Create the base window
        self.gameProcess = None
        self.windowExists = True
        self.root = Tk()
        self.root.title(c.WINDOW_TITLE)
        self.root.protocol("WM_DELETE_WINDOW", self.onClose)
        addIcon(self.root)

        self.mainWindowFrame = ttk.Frame(self.root)
        self.mainWindowFrame.grid(row=0, column=0, sticky="NSEW")

        self.root.grid_rowconfigure(4, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # File prompts
        self.exeFileRow = filePromptWithHistory(
            self.mainWindowFrame,
            0,
            0,
            c.EXE_FILE_PROMPT,
            True,
            [("Executable files", "*.exe"), ("All files", "*.*")],
            "*.exe",
            False,
            self,
        )
        self.dataWinFileRow = filePromptWithHistory(
            self.mainWindowFrame,
            1,
            0,
            c.DATAWIN_FILE_PROMPT,
            True,
            [("*.win files", "*.win"), ("All files", "*.*")],
            "*.win",
            False,
            self,
        )
        self.movieFileRow = filePromptWithHistory(
            self.mainWindowFrame,
            2,
            0,
            c.MOVIE_FILE_PROMPT,
            False,
            [("GMReplay files", "*.gmr"), ("All files", "*.*")],
            "*.gmr",
            False,
            self,
        )

        # Record/play buttons
        self.recordPlayRow = recordPlayRadioButtons(
            self.mainWindowFrame,
            3,
            0,
            c.RECORDING_STRING,
            c.PLAYBACK_STRING,
            c.START_STRING,
            c.STOP_STRING,
            self,
        )

        # Debug button
        # self.debugButton = ttk.Button(self.mainWindowFrame, text="Test", command=debugFunction)))
        # self.debugButton.grid(column=11, row=3, padx=c.GLOBAL_PADDING, pady=c.GLOBAL_PADDING)

        # Create the input window
        self.inputWindowFrame = ttk.Frame(self.root)
        self.inputWindowFrame.grid(row=4, column=0, sticky="NSEW")

        self.inputGridObj = inputSheetClass(self.inputWindowFrame, 0, 0, self)

        # Raw input display. Useful for debugging, but not meant for end users.
        # TODO: Allow enabling this through config
        # self.inputRawRadioButtonObj = inputRawRadioButtons(self.mainWindowFrame, 3, 4, c.INPUTS_STRING, c.RAW_HIDE_STRING, c.RAW_SHOW_STRING, self)

        # Menu bar
        self.menuBar = Menu(self.root)
        self.fileMenu = Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label=c.SAVE_OPTION_STRING, command=self.saveMovieInputs)
        self.fileMenu.add_command(label=c.SAVE_AS_OPTION_STRING, command=self.saveAsCommand)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label=c.PREFERENCES_STRING, command=self.preferencesWindow)
        self.menuBar.add_cascade(label="File", menu=self.fileMenu)

        self.helpMenu = Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label="About GMReplay...", command=self.aboutWindow)
        self.menuBar.add_cascade(label="Help", menu=self.helpMenu)

        self.root.config(menu=self.menuBar)

        # Run these once to draw all the window elements while the movie is loading
        self.root.update_idletasks()
        self.root.update()

        # Load history/last movie after everything else has been initialized
        for filePrompt in (self.exeFileRow, self.dataWinFileRow, self.movieFileRow):
            if len(filePrompt.history) > 0:
                filePrompt.comboboxVar.set(filePrompt.history[0])

    def areAllFilesSelected(self):
        try:
            return (
                self.exeFileRow.combobox.get() != ""
                and self.dataWinFileRow.combobox.get() != ""
                and self.movieFileRow.combobox.get() != ""
            )
        # The three objects don't exist yet
        except AttributeError:
            return False

    def loadMovieInputs(self, movieFilePath):
        return self.inputGridObj.loadMovieInputs(movieFilePath)

    def saveMovieInputs(self, movieFilePath=None):
        if movieFilePath is None:
            movieFilePath = self.movieFileRow.combobox.get()
        return self.inputGridObj.saveMovieInputs(movieFilePath)

    def saveAsCommand(self):
        return self.saveMovieInputs(
            self.movieFileRow.browseFile(
                c.SAVE_AS_OPTION_STRING,
                [("GMReplay files", "*.gmr"), ("All files", "*.*")],
                "*.gmr",
                fileExists=False,
            )
        )

    def clearFileHistory(self):
        # Set config
        self.config.File_History.data_win = []
        self.config.File_History.game_exe = []
        self.config.File_History.movie = []
        configSave(self.config, c.CONFIG_PATH)

        # Set history
        self.dataWinFileRow.history = []
        self.exeFileRow.history = []
        self.movieFileRow.history = []

        # Set combobox
        self.dataWinFileRow.comboboxVar.set("")
        self.exeFileRow.comboboxVar.set("")
        self.movieFileRow.comboboxVar.set("")
        self.dataWinFileRow.combobox["values"] = self.dataWinFileRow.history
        self.exeFileRow.combobox["values"] = self.exeFileRow.history
        self.movieFileRow.combobox["values"] = self.movieFileRow.history

    def updateMaxHistory(self, var, index, mode):
        # Set config
        self.config.File_History.maxhistoryentries = str(self.maxHistorySpinboxVar.get())
        configSave(self.config, c.CONFIG_PATH)

    def suppressGameOutputUpdate(self):
        self.config.General.suppress_game_debug_output = self.suppressGameOutputCheckbuttonVar.get()
        configSave(self.config, c.CONFIG_PATH)

    def preferencesWindow(self):
        prefWindowRoot = Toplevel(self.root)
        prefWindowRoot.title(c.PREFERENCES_WINDOW_TITLE)
        addIcon(prefWindowRoot)

        pad = c.GLOBAL_PADDING

        # Organize these later. For now just make a hodgepodge of various config options
        maxHistoryLabel = Label(prefWindowRoot, text=c.MAX_HISTORY_STRING)
        maxHistoryLabel.grid(row=0, column=0, padx=pad, pady=pad)

        self.maxHistorySpinboxVar = IntVar(value=self.config.File_History.maxhistoryentries)
        self.maxHistorySpinboxVar.trace_add("write", self.updateMaxHistory)

        maxHistorySpinbox = ttk.Spinbox(
            prefWindowRoot, width=5, from_=0, to=100, increment=1, textvariable=self.maxHistorySpinboxVar
        )
        maxHistorySpinbox.grid(row=0, column=1, padx=pad, pady=pad)

        clearHistoryButton = ttk.Button(prefWindowRoot, text=c.CLEAR_HISTORY_STRING, command=self.clearFileHistory)
        clearHistoryButton.grid(row=0, column=2, padx=pad, pady=pad)

        self.suppressGameOutputCheckbuttonVar = StringVar(value=self.config.General.suppress_game_debug_output)
        suppressGameOutputCheckbutton = ttk.Checkbutton(
            prefWindowRoot,
            text=c.SUPPRESS_GAME_OUTPUT_STRING,
            variable=self.suppressGameOutputCheckbuttonVar,
            offvalue="False",
            onvalue="True",
            command=self.suppressGameOutputUpdate,
        )
        suppressGameOutputCheckbutton.grid(row=1, column=0, padx=pad, pady=pad)

    def aboutWindow(self):
        aboutWindowRoot = Toplevel(self.root)
        aboutWindowRoot.title(c.ABOUT_WINDOW_TITLE)
        aboutWindowRoot.geometry("730x417")
        addIcon(aboutWindowRoot)
        width = 730

        pad = c.GLOBAL_PADDING

        self.iconImage = PhotoImage(file="img/gmreplay_logo.gif")
        iconLabel = Label(aboutWindowRoot, image=self.iconImage)
        iconLabel.pack(side="top", fill="none", expand=False, padx=pad, pady=pad)

        headerLabel = Label(
            aboutWindowRoot,
            text=c.STARTUP_STRING,
            wraplength=width - (pad * 2),
            anchor="w",
            justify="center",
        )
        headerLabel.pack(side="top", fill="none", expand=False, padx=pad, pady=pad)

        firstLabel = Label(
            aboutWindowRoot,
            text=c.ABOUT_MESSAGE,
            wraplength=width - (pad * 2),
            anchor="w",
            justify="left",
        )
        firstLabel.pack(side="top", fill="both", expand=True, padx=pad, pady=pad)

        firstLabelHyperlink = Label(
            aboutWindowRoot,
            text=c.ABOUT_LINK,
            cursor="hand2",
            foreground="blue",
            anchor="w",
            justify="center",
        )
        firstLabelHyperlink.pack(side="top", fill="none", expand=False, padx=pad, pady=pad)
        firstLabelHyperlink.bind("<Button-1>", lambda e: openURL(c.ABOUT_LINK))

        secondLabel = Label(
            aboutWindowRoot,
            text=c.LICENSE_HEADER,
            wraplength=width - (pad * 2),
            anchor="w",
            justify="left",
        )
        secondLabel.pack(side="top", fill="both", expand=True, padx=pad, pady=pad)

        secondLabelHyperlink = Label(
            aboutWindowRoot,
            text=c.LICENSE_LINK,
            cursor="hand2",
            foreground="blue",
            anchor="w",
            justify="center",
        )
        secondLabelHyperlink.pack(side="top", fill="none", expand=False, padx=pad, pady=pad)
        secondLabelHyperlink.bind("<Button-1>", lambda e: openURL(c.LICENSE_LINK))

    def onClose(self):
        print(c.EXIT_STRING)
        self.windowExists = False
        self.root.destroy()


class filePromptWithHistory:
    """
    Consists of a label, a combo box, and a browse button. Keeps track of history in the config file.
    """

    def __init__(
        self,
        frame,
        rowOffset,
        columnOffset,
        promptText,
        fileExists,
        extensions,
        defaultExtension,
        isFolder,
        mainWindowObj,
    ):
        self.frame = frame
        self.mainWindowObj = mainWindowObj
        pad = c.GLOBAL_PADDING
        self.fileExists = fileExists
        self.promptText = promptText

        self.history = self.loadHistory()
        self.isFolder = isFolder

        # Create the label
        self.label = ttk.Label(frame, text=promptText)
        self.label.grid(column=0 + columnOffset, row=0 + rowOffset, sticky="E", padx=pad, pady=pad)

        self.comboboxVar = StringVar(value=self.history[0])

        self.comboboxVar.trace_add("write", self.onFieldChange)

        # Create the combo box
        self.combobox = ttk.Combobox(frame, values=self.history, textvariable=self.comboboxVar, width=80)
        self.combobox.grid(
            column=1 + columnOffset,
            row=0 + rowOffset,
            padx=pad,
            pady=pad,
            sticky="EW",
            columnspan=10,
        )

        # Create the browse button
        self.button = ttk.Button(
            frame,
            text="Browse...",
            command=lambda: self.browseFile(promptText, extensions, defaultExtension),
        )
        self.button.grid(column=11 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="E")

        # Only the combo box should be resizable
        frame.grid_columnconfigure(0 + columnOffset, weight=0)
        frame.grid_columnconfigure(10 + columnOffset, weight=1)
        frame.grid_columnconfigure(11 + columnOffset, weight=0)

    def browseFile(
        self,
        promptText,
        extensions=None,
        defaultExtension="*.gmr",
        fileExists=None,
    ):
        # This searches for a file and adds it to the combo box history
        if extensions is None:
            extensions = [
                ("All files", "*.*"),
                ("GMReplay files", "*.gmr"),
                ("Executable files", "*.exe"),
                ("*.win files", "*.win"),
            ]
        if fileExists is None:
            fileExists = self.fileExists
        filePath = (
            filedialog.askopenfilename(
                parent=self.frame,
                title=promptText,
                defaultextension=defaultExtension,
                filetypes=extensions,
            )
            if fileExists
            else filedialog.asksaveasfilename(
                parent=self.frame,
                title=promptText,
                defaultextension=defaultExtension,
                filetypes=extensions,
            )
        )
        if filePath:
            self.combobox.set(filePath)
            self.addToHistory(filePath)
        return filePath

    def addToHistory(self, filePath):
        # Add the file path to history if it's not already there,
        # and also run some checks for actions to be completed when a file is selected
        if filePath not in self.history:
            self.history.insert(0, filePath)

            # Restrict number of entries
            self.history = self.history[: int(self.mainWindowObj.config.File_History.maxhistoryentries)]

            self.combobox["values"] = self.history

            # Update the configuration and save
            match self.promptText:
                case c.EXE_FILE_PROMPT:
                    self.mainWindowObj.config.File_History.game_exe = self.history
                case c.DATAWIN_FILE_PROMPT:
                    self.mainWindowObj.config.File_History.data_win = self.history
                case c.MOVIE_FILE_PROMPT:
                    self.mainWindowObj.config.File_History.movie = self.history

            configSave(self.mainWindowObj.config, c.CONFIG_PATH)

        # If the exe was just selected, try to select the data.win by default
        if self.promptText == c.EXE_FILE_PROMPT:
            dataWinDefaultPath = folder(self.mainWindowObj.exeFileRow.combobox.get()) + "/data.win"
            if path.isfile(dataWinDefaultPath):
                self.mainWindowObj.dataWinFileRow.addToHistory(dataWinDefaultPath)
                self.mainWindowObj.dataWinFileRow.combobox.set(dataWinDefaultPath)

        # If all three files have been selected, enable the start buttons
        if self.mainWindowObj.areAllFilesSelected():
            self.mainWindowObj.recordPlayRow.enableStart()

    def loadHistory(self):
        ## Loads the history from appdata
        match self.promptText:
            case c.EXE_FILE_PROMPT:
                self.history = self.mainWindowObj.config.File_History.game_exe
            case c.DATAWIN_FILE_PROMPT:
                self.history = self.mainWindowObj.config.File_History.data_win
                # Since this loads after the exe file, we should do the updates now
                dataWinDefaultPath = folder(self.mainWindowObj.exeFileRow.combobox.get()) + "/data.win"
                if path.isfile(dataWinDefaultPath):
                    self.addToHistory(dataWinDefaultPath)
            case c.MOVIE_FILE_PROMPT:
                self.history = self.mainWindowObj.config.File_History.movie

        return self.history

    def onFieldChange(self, var, index, mode):
        if path.isfile(self.comboboxVar.get()):
            self.addToHistory(self.comboboxVar.get())
            if self.promptText == c.MOVIE_FILE_PROMPT:
                self.mainWindowObj.loadMovieInputs(self.comboboxVar.get())


class recordPlayRadioButtons:
    """
    The record and play radio buttons and the start button.
    """

    def __init__(
        self,
        frame,
        rowOffset,
        columnOffset,
        recordText,
        playbackText,
        startText,
        stopText,
        mainWindowObj,
    ):
        self.mainWindowObj = mainWindowObj
        self.frame = frame

        self.recordPlayVar = IntVar(frame, c.RECORD)

        pad = c.GLOBAL_PADDING

        self.recordRadioButton = ttk.Radiobutton(
            frame,
            text=recordText,
            value=c.RECORD,
            variable=self.recordPlayVar,
            command=self.radioButtonInteract,
        )
        self.recordRadioButton.grid(column=0 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        self.playRadioButton = ttk.Radiobutton(
            frame,
            text=playbackText,
            value=c.PLAY,
            variable=self.recordPlayVar,
            command=self.radioButtonInteract,
        )
        self.playRadioButton.grid(column=1 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        self.startButton = ttk.Button(
            frame,
            text=startText,
            command=lambda: self.recordOrPlayMovie(self.recordPlayVar.get()),
        )
        self.startButton.grid(column=2 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        self.stopButton = ttk.Button(frame, text=stopText, command=self.stopButtonInteract)
        self.stopButton.grid(column=3 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        frame.grid_columnconfigure(0 + columnOffset, weight=0)
        frame.grid_columnconfigure(1 + columnOffset, weight=0)
        frame.grid_columnconfigure(2 + columnOffset, weight=0)

        # Disable Start if the files aren't selected (they can be selected from history)
        if self.mainWindowObj.areAllFilesSelected() is False:
            self.disableStart()

        # Alwyas disable Stop on init
        self.disableStop()

    def recordOrPlayMovie(self, selection):
        ## Handles recording (selection is 1 aka RECORD) or playback (selection is 2 aka PLAY)

        # Attempt to patch the exe file
        pathToExe = genPatchedExe(self.mainWindowObj.exeFileRow.combobox.get())

        # Save the movie if it's in playback mode
        if selection == c.PLAY:
            self.mainWindowObj.saveMovieInputs()

        # Run the game with the record command
        print(c.GAME_START_STRING)
        # This one hides the console output
        if self.mainWindowObj.config.General.suppress_game_debug_output == "True":
            self.mainWindowObj.gameProcess = subprocess.Popen(
                [
                    pathToExe,
                    ("-record" if selection == c.RECORD else "-playback"),
                    self.mainWindowObj.movieFileRow.combobox.get(),
                    "-game",
                    self.mainWindowObj.dataWinFileRow.combobox.get(),
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
            )

        # This one shows the console output
        else:
            self.mainWindowObj.gameProcess = subprocess.Popen(
                [
                    pathToExe,
                    ("-record" if selection == c.RECORD else "-playback"),
                    self.mainWindowObj.movieFileRow.combobox.get(),
                    "-game",
                    self.mainWindowObj.dataWinFileRow.combobox.get(),
                    "-debugoutput",
                    getcwd() + "\\debugoutput.log",
                    "|",
                    "cat",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            # Prevent blocking of the game process
            set_blocking(self.mainWindowObj.gameProcess.stdout.fileno(), False)

        # Disable Start, enable Stop, disable radio buttons
        self.movieStart()

    def enableStart(self):
        # Enable the start button
        self.startButton.config(state="enabled")

    def disableStart(self):
        # Disable the start button
        self.startButton.config(state="disabled")

    def enableRadio(self):
        # Enable the radio buttons
        self.recordRadioButton.config(state="enabled")
        self.playRadioButton.config(state="enabled")

    def disableRadio(self):
        # Disable the radio buttons
        self.recordRadioButton.config(state="disabled")
        self.playRadioButton.config(state="disabled")

    def enableStop(self):
        # Enable the stop button
        self.stopButton.config(state="enabled")

    def disableStop(self):
        # Disable the stop button
        self.stopButton.config(state="disabled")

    def movieStart(self):
        # Commands to run when the movie starts
        self.disableStart()
        self.enableStop()
        self.disableRadio()

    def movieEnd(self):
        # Commands to run when the movie ends
        if self.mainWindowObj.areAllFilesSelected():
            self.enableStart()
        self.disableStop()
        self.enableRadio()
        # Only reload the movie if we were recording
        if self.recordPlayVar.get() == c.RECORD:
            self.mainWindowObj.inputGridObj.loadMovieInputs()

    def radioButtonInteract(self):
        # Make it prompt for opening or saving based on the button
        self.mainWindowObj.movieFileRow.fileExists = self.recordPlayVar.get() == c.PLAY

    def stopButtonInteract(self):
        # Commands to run when the stop button is pressed
        print(c.GAME_STOP_STRING)
        self.mainWindowObj.gameProcess.terminate()
        # Movie end will be triggered by detecting the killed process, to prevent loading the movie twice


class inputRawRadioButtons:
    """
    The record and play radio buttons and the start button.
    """

    def __init__(
        self,
        frame,
        rowOffset,
        columnOffset,
        inputText,
        rawHideText,
        rawShowText,
        mainWindowObj,
    ):
        self.mainWindowObj = mainWindowObj
        self.frame = frame

        self.inputRawVar = StringVar(frame, inputText)

        pad = c.GLOBAL_PADDING

        self.inputRawLabel = ttk.Label(frame, text=c.INPUT_RAW_LABEL)
        self.inputRawLabel.grid(column=0 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        self.inputRadioButton = ttk.Radiobutton(
            frame,
            text=inputText,
            value=inputText,
            variable=self.inputRawVar,
            command=self.radioButtonInteract,
        )
        self.inputRadioButton.grid(column=1 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        self.rawHideRadioButton = ttk.Radiobutton(
            frame,
            text=rawHideText,
            value=rawHideText,
            variable=self.inputRawVar,
            command=self.radioButtonInteract,
        )
        self.rawHideRadioButton.grid(column=2 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

        self.rawShowRadioButton = ttk.Radiobutton(
            frame,
            text=rawShowText,
            value=rawShowText,
            variable=self.inputRawVar,
            command=self.radioButtonInteract,
        )
        self.rawShowRadioButton.grid(column=3 + columnOffset, row=0 + rowOffset, padx=pad, pady=pad, sticky="NE")

    def radioButtonInteract(
        self,
    ):  # Make it prompt for opening or saving based on the button
        self.mainWindowObj.inputGridObj.displayType = self.inputRawVar.get()
        self.mainWindowObj.inputGridObj.updateInputEditor()


class inputSheetClass:
    """
    A class for using Tksheet for the input display
    """

    def __init__(
        self,
        inputWindowFrame,
        rowOffset,
        columnOffset,
        mainWindowObj,
        loadedMovieData=None,
    ):
        if loadedMovieData is None:
            loadedMovieData = []
        self.mainWindowObj = mainWindowObj
        self.inputWindowFrame = inputWindowFrame
        self.rowOffset = rowOffset
        self.columnOffset = columnOffset
        self.inputFormatMovieData = []
        self.keyCodesList = []
        self.loadedMovieData = loadedMovieData
        self.inputColumnsList = c.DEFAULT_COLUMNS_LIST
        self.rawColumnsList = c.DEFAULT_COLUMNS_LIST_RAW
        self.rawMovieData = []
        self.displayType = c.INPUTS_STRING
        self.lastClickR = -1
        self.lastClickC = -1
        self.dragged = False

        pad = c.GLOBAL_PADDING

        # Initialize the sheet object with the column labels
        self.sheet = Sheet(
            self.inputWindowFrame,
            headers=self.inputColumnsList,
            data=self.inputFormatMovieData,
            align="center",
            after_redraw_time_ms=0,
        )
        self.sheet.enable_bindings(c.SHEET_BINDINGS)
        self.sheet.extra_bindings("cell_select", self.onLeftClick)
        self.sheet.extra_bindings(("drag_select_cells", "shift_cell_select"), self.onDrag)
        self.sheet.bind("<ButtonRelease-1>", self.onLeftRelease)
        self.sheet.bind("<Double-Button-1>", self.onDoubleClick)
        self.sheet.extra_bindings("end_edit_cell", self.onEndEditCell)
        self.sheet.extra_bindings(("end_insert_row", "end_delete_rows"), self.onBigSheetUpdate)
        self.sheet.edit_validation(self.validateNumericInput)
        self.sheet.extra_bindings("begin_add_column", self.columnSelection)
        # Add a menu to the column headers and redirect it to our column selection command
        self.sheet.MT.menu_add_command(
            self.sheet.CH.ch_rc_popup_menu,
            label=c.INSERT_COLUMN_TEXT,
            command=self.columnSelection,
        )

        self.sheet.pack(side="top", fill="both", expand=True, padx=pad, pady=pad)

    def updateInputGrid(self, inputFormatMovieData):
        self.sheet.set_sheet_data(inputFormatMovieData, redraw=False)

    def updateColumnLabels(self, columnsList):
        self.sheet.headers(columnsList, redraw=False)

    def updateColumnWidths(self, columnsList):
        ## Updates the column widths of self.sheet, a workaround because set_all_cell_sizes_to_text doesn't take headers into account
        ## and doesn't add enough padding to small columns

        # First set all columns to the smallest value
        self.sheet.set_all_column_widths(c.COLUMN_SMALL_WIDTH, redraw=False)

        # Resize if it was too small with one of the five default widths. TODO: Make this not look like Toby Fox wrote it.
        for i in range(len(columnsList)):
            if (thisWidth := self.sheet.get_column_text_width(column=i)) > c.COLUMN_SMALL_WIDTH:
                if thisWidth > c.COLUMN_MEDIUM_WIDTH:
                    if thisWidth > c.COLUMN_BIG_WIDTH:
                        if thisWidth > c.COLUMN_VERYBIG_WIDTH:
                            self.sheet.column_width(i, c.COLUMN_MASSIVE_WIDTH, redraw=False)
                        else:
                            self.sheet.column_width(i, c.COLUMN_VERYBIG_WIDTH, redraw=False)
                    else:
                        self.sheet.column_width(i, c.COLUMN_BIG_WIDTH, redraw=False)
                else:
                    self.sheet.column_width(i, c.COLUMN_MEDIUM_WIDTH, redraw=False)

    def loadMovieInputs(self, movieFilePath=None):
        # If a movie file path wasn't given, use the previous one
        if movieFilePath is not None:
            # Assign the movieFilePath to self
            self.movieFilePath = movieFilePath

        # Make sure it's a real path
        if self.movieFilePath != "":
            print(c.LOADING_MOVIE_STRING)
            # Parse the inpts
            self.loadedMovieData = loadMovie(self.movieFilePath)
            # Takes the loaded inputs, rotates them (rows become columns and vice versa), applies a recursive bitwise or
            # operation to determine which columns have nonzero values, then uses compress to condense the default columns list into the displayed columns list
            self.rawBoolMask = reduceBitwiseOr(rotate2DArray(self.loadedMovieData))
            self.rawColumnsList = list(compress(c.DEFAULT_COLUMNS_LIST_RAW, self.rawBoolMask))
            # Apply the boolean mask to the rotated movie data and then rotate it back
            self.rawMovieData = rotate2DArray(list(compress(rotate2DArray(self.loadedMovieData), self.rawBoolMask)))

            self.inputColumnsList, self.keyCodesList, self.inputFormatMovieData = recordingToInputs(
                self.loadedMovieData
            )

            self.updateInputEditor()

            # Update the main window and then print the completion message
            self.mainWindowObj.root.update_idletasks()
            self.mainWindowObj.root.update()

            print(c.MOVIE_LOADED_STRING)

    def saveMovieInputs(self, movieFilePath=None):
        # If a movie file path wasn't given, use the previous one
        if movieFilePath is not None:
            # Assign the movieFilePath to self
            self.movieFilePath = movieFilePath
        # Make sure it's a real path
        if self.movieFilePath != "":
            print(c.SAVE_MOVIE_STRING)

            self.getInputGridUpdates()  # Updates self.inputFormatMovieData, self.rawMovieData, self.loadedMovieData

            if self.displayType == c.INPUTS_STRING:
                self.loadedMovieData = inputsToRecording(
                    self.inputColumnsList, self.keyCodesList, self.inputFormatMovieData
                )

            # Otherwise the loaded movie data should have already been updated
            saveMovie(self.movieFilePath, self.loadedMovieData)

            print(c.SAVED_MOVIE_STRING)

    def updateInputEditor(self):
        print(c.UPDATE_INPUT_EDITOR_STRING)
        # Select between input and raw mode
        if self.displayType == c.INPUTS_STRING:
            # Update the columns list and the input grid with the appropriate data
            self.updateInputGrid(self.inputFormatMovieData)
            self.updateColumnLabels(self.inputColumnsList)
            self.updateColumnWidths(self.inputColumnsList)

        elif self.displayType == c.RAW_HIDE_STRING:
            # Update the columns list and the input grid with the appropriate data
            self.updateInputGrid(stringify(self.rawMovieData))
            self.updateColumnLabels(self.rawColumnsList)
            self.updateColumnWidths(self.rawColumnsList)

        elif self.displayType == c.RAW_SHOW_STRING:
            # Update the columns list and the input grid with the appropriate data
            self.updateInputGrid(stringify(self.loadedMovieData))
            self.updateColumnLabels(c.DEFAULT_COLUMNS_LIST_RAW)
            self.updateColumnWidths(c.DEFAULT_COLUMNS_LIST_RAW)

        # Redraw
        self.sheet.redraw()
        print(c.INPUT_EDITOR_UPDATED_STRING)

    def getInputGridUpdates(self):
        # Retrieve the entire input grid and put it back into the loaded data.
        # TODO: This is an expensive operation, so it should be replaced with incremental updates.
        if self.displayType == c.INPUTS_STRING:
            self.inputFormatMovieData = self.sheet.get_sheet_data()

        elif self.displayType == c.RAW_HIDE_STRING or self.displayType == c.RAW_SHOW_STRING:
            # Not implemented
            pass

    def columnSelection(self):
        ## Open a window prompting selection of which columns to show
        if self.displayType != c.INPUTS_STRING:
            return None  # This operation only applies to input display mode

        pad = c.GLOBAL_PADDING
        maxElementsPerRow = 10

        # Make a new window
        self.columnSelectionWindowRoot = Toplevel(self.mainWindowObj.root)
        self.columnSelectionWindowRoot.title(c.SELECT_COLUMNS_TITLE_STRING)
        addIcon(self.columnSelectionWindowRoot)

        instructionsLabel = Label(
            self.columnSelectionWindowRoot,
            text=c.SELECT_COLUMNS_STRING,
            anchor="w",
            justify="left",
        )
        instructionsLabel.grid(
            row=0,
            column=0,
            padx=pad,
            pady=pad,
            columnspan=maxElementsPerRow,
            sticky="w",
        )

        self.checkButtons = []
        self.checkButtonVars = []
        thisRow = 1
        elementsInRow = 0

        for value in c.VK_NAMES.values():
            if value not in self.inputColumnsList and value != "":
                # Create a check button for this column
                self.checkButtonVars += [StringVar(value="")]
                self.checkButtons += [
                    ttk.Checkbutton(
                        self.columnSelectionWindowRoot,
                        text=value,
                        variable=self.checkButtonVars[-1],
                        offvalue="",
                        onvalue=value,
                    )
                ]
                self.checkButtons[-1].grid(row=thisRow, column=elementsInRow, padx=pad, pady=pad, sticky="w")
                elementsInRow += 1
                if elementsInRow >= maxElementsPerRow:
                    thisRow += 1
                    elementsInRow = 0

        columnSelectionOkButton = ttk.Button(
            self.columnSelectionWindowRoot,
            text=c.OK_STRING,
            command=self.closeColumnSelector,
        )
        columnSelectionOkButton.grid(row=thisRow + 2, column=0, padx=pad, pady=pad, columnspan=maxElementsPerRow)

        # Now cancel the user-initiated column addition
        return None

    def closeColumnSelector(self):
        print(
            c.ADDING_COLUMNS_STRING
            + "".join(thisVar.get() + ", " for thisVar in self.checkButtonVars if thisVar.get() != "")[:-2]
        )
        # Take the selected columns and add them to the input editor
        newStrList = []
        for var in self.checkButtonVars:
            if (thisStr := var.get()) != "":
                # Add this column
                newStrList += [keyCodes(thisStr)]
                self.keyCodesList += [keyCodes(thisStr)]

        # Exit the column selection window
        self.columnSelectionWindowRoot.destroy()

        # Sort keyCodesList
        self.keyCodesList.sort()

        # Record the added columns
        addedColumnIndices = []
        for thisStr in newStrList:
            addedColumnIndices += [self.keyCodesList.index(thisStr)]

        inputKeynameColumnLabels = [""] * len(self.keyCodesList)

        # Convert the input column labels to names
        for i in range(len(inputKeynameColumnLabels)):
            inputKeynameColumnLabels[i] = keyName(self.keyCodesList[i])

        # Now check if mouse wheel was used
        if (
            len(self.inputColumnsList) >= 4 and "wheel" in self.inputColumnsList[-4]
        ):  # Two wheel columns for a total of four end columns
            self.inputColumnsList = inputKeynameColumnLabels + self.inputColumnsList[-4:]
        elif (
            len(self.inputColumnsList) >= 3 and "wheel" in self.inputColumnsList[-3]
        ):  # One wheel column for a total of three end columns
            self.inputColumnsList = inputKeynameColumnLabels + self.inputColumnsList[-3:]
        else:  # No wheel columns for a total of two end columns
            self.inputColumnsList = inputKeynameColumnLabels + self.inputColumnsList[-2:]

        # Add blank columns to the input data, ensuring they're done in order
        addedColumnIndices.sort()
        rotatedInputData = rotate2DArray(self.inputFormatMovieData)
        for index in addedColumnIndices:
            rotatedInputData.insert(index, [""] * len(self.inputFormatMovieData))

        self.inputFormatMovieData = rotate2DArray(rotatedInputData)

        # Now we have what we need to update the input grid
        self.updateInputEditor()

    def onDrag(self, eventDict):
        if self.displayType == c.INPUTS_STRING:
            # First set the flag indicating that a drag has happened
            self.dragged = True

            # Handle cell painting
            if self.displayType != c.INPUTS_STRING:  # Raw mode is read-only
                return

            # First find the origin row and column
            originRow = self.lastClickR
            originColumn = self.lastClickC

            # Now find the destination row. Single-column painting only, to match libTAS behavior.
            # We want to go to where the mouse is now, not just the top of the selection
            destRow = (
                eventDict["being_selected"].upto_r
                if eventDict["being_selected"].upto_r - 1 != originRow
                else eventDict["being_selected"].from_r
            )

            # Number of rows to fill
            numRows = max(originRow + 1, destRow) - min(originRow, destRow)

            # Now update every cell in between
            # First find the origin cell's value
            originValue = self.originValue

            # Find the new value
            if originColumn == len(self.inputColumnsList) - 1 or originColumn == len(self.inputColumnsList) - 2:
                # Numeric columns so newValue should be the same
                newValue = originValue
            else:
                # Boolean columns so newValue should be the opposite
                if originValue == "":  # noqa: SIM108 (reason: recommendation is less readable)
                    newValue = self.inputColumnsList[originColumn]
                else:
                    newValue = ""

            # Now make a span
            overwriteSpan = self.sheet[min(originRow, destRow), originColumn]

            # Overwrite the data down the column
            overwriteSpan.transpose().data = [newValue for i in range(numRows)]

            # Now update the 2d array
            for index in range(originRow, destRow):
                self.inputFormatMovieData[index][originColumn] = newValue

    def onLeftClick(self, eventDict):
        if self.displayType == c.INPUTS_STRING:
            # Check if this is a shift-click
            # TODO: use a shift click binding instead
            if eventDict["being_selected"] != ():
                return

            # Clear the dragged flag
            self.dragged = False

            self.lastClickR = next(iter(eventDict["selection_boxes"])).from_r
            self.lastClickC = next(iter(eventDict["selection_boxes"])).from_c

            # Set the origin value
            self.originValue = self.sheet[self.lastClickR, self.lastClickC].data

    def onLeftRelease(self, event):
        if self.displayType == c.INPUTS_STRING and self.dragged is False:
            overwriteSpan = self.sheet[self.lastClickR, self.lastClickC]

            # Figure out if it's a numeric input (mouseX, mouseY) or not
            # Check if they're in the last two columns which are mouseX and mouseY
            # TODO: Handle this more flexibly to allow for future numeric inputs
            if self.lastClickC == len(self.inputColumnsList) - 1 or self.lastClickC == len(self.inputColumnsList) - 2:
                return  # We don't handle this here

            # If it's blank, set it to the column label.
            elif overwriteSpan.data == "":
                overwriteSpan.data = self.inputColumnsList[self.lastClickC]
                self.inputFormatMovieData[self.lastClickR][self.lastClickC] = self.inputColumnsList[self.lastClickC]

            # Otherwise, figure out if it's a numeric input (mouseX, mouseY) or not
            # Check if they're in the last two columns which are mouseX and mouseY
            # TODO: Handle this more flexibly to allow for future numeric inputs
            elif self.lastClickC == len(self.inputColumnsList) - 1 or self.lastClickC == len(self.inputColumnsList) - 2:
                return  # We don't handle this here

            # Otherwise, clear the data
            else:
                overwriteSpan.clear()
                self.inputFormatMovieData[self.lastClickR][self.lastClickC] = ""

    def onEndEditCell(self, eventDict):
        self.inputFormatMovieData[self.lastClickR][self.lastClickC] = int(
            self.sheet[self.lastClickR, self.lastClickC].data
        )

    def onDoubleClick(self, eventDict):
        # Allow edits on the numeric columns (two rightmose columns in the input editor)
        if self.displayType == c.INPUTS_STRING and (
            self.lastClickC == len(self.inputColumnsList) - 1 or self.lastClickC == len(self.inputColumnsList) - 2
        ):
            self.sheet.MT.open_cell(eventDict)

    def onBigSheetUpdate(self, eventDict):
        self.getInputGridUpdates()

    def validateNumericInput(self, event):
        if event.value.isdigit():
            # The input is validated, so return event.value
            return event.value
        else:
            # Bad input, so cancel the user edit by returning None
            print(c.INVALID_INPUT_STRING)
            return None


def addIcon(root):
    """
    Add the GMReplay icon to the input Tkinter root instance

    Args:
        root (Any): Tkinter root instance to add the logo
    """
    root.iconbitmap("img/gmreplay_logo.ico")
