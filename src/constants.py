# Built-in packages
from os import getenv, path

# Constants to be used globally
MIN_PYTHON = (3, 12)
RECORD = 1
PLAY = 2
APPDATA_PATH = path.join(getenv("APPDATA", ""), "GMReplay")

# Strings

# Main program strings
VERSION_NUMBER = "v0.1.6"
STARTUP_STRING = "GMReplay " + VERSION_NUMBER + " by OceanBagel\n"
MIN_PYTHON_STRING = f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]} or later is required.\n"
LICENSE_HEADER = (
    "Copyright (C) 2024 OceanBagel\n\n"
    + "This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License "
    + "as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. "
    + "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty "
    + "of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. "
    + "You should have received a copy of the GNU General Public License along with this program. If not, see:"
)
LICENSE_LINK = "https://www.gnu.org/licenses/"
CONFIG_FILENAME = "config.ini"
CONFIG_PATH = path.join(APPDATA_PATH, CONFIG_FILENAME)

# Patching strings
PATCH_FILE_NAME = "__temp_GMR_patched_runner.exe"
PATCH_START_STRING = "Patching mouse inputs..."
PATCH_MOUSE_FAIL_STRING = "WARNING: Patching encountered an issue. Mouse inputs will not work."
PATCH_MOUSE_SUCCESS_STRING = "Mouse inputs patched successfully."
PATCH_KEYDIRECT_STRING = "Patching keyboard_check_direct()..."
PATCH_KEYDIRECT_FAIL_STRING = "WARNING: Patching encountered an issue. Direct keyboard input will not work."
PATCH_KEYDIRECT_SUCCESS_STRING = "keyboard_check_direct() patched successfully."
PATCH_RANDOMIZE_STRING = "Patching randomize()..."
PATCH_RANDOMIZE_FAIL_STRING = "WARNING: Patching encountered an issue. Randomness will not be deterministic."
PATCH_RANDOMIZE_SUCCESS_STRING = "randomize() patched successfully."
PATCH_SUCCESS_STRING = "Runner patched successfully."

# UI strings
WINDOW_TITLE = "GMReplay " + VERSION_NUMBER
ABOUT_WINDOW_TITLE = "About GMReplay"
PREFERENCES_WINDOW_TITLE = "Preferences"
INPUT_WINDOW_SUFFIX = " - Input Editor"
EXE_FILE_PROMPT = "Game executable:"
DATAWIN_FILE_PROMPT = "Game data.win file:"
MOVIE_FILE_PROMPT = "Movie file:"
RECORDING_STRING = "Recording"
PLAYBACK_STRING = "Playback"
START_STRING = "Start"
STOP_STRING = "Stop"
GAME_START_STRING = "Starting the game..."
GAME_STOP_STRING = "Stopping the game..."
GAME_CLOSED_STRING = "Game was closed."
DEFAULT_COLUMNS_LIST_RAW = [
    "lastChar",
    "inputString",
    "lastKey",
    "currentKey",
    "keyDown",
    "keyReleased",
    "keyPressed",
    "lastButton",
    "currentButton",
    "buttonDown",
    "buttonReleased",
    "buttonPressed",
    "wheelUp",
    "wheelDown",
    "mousePos",
    "mouseX",
    "mouseY",
]
DEFAULT_COLUMNS_LIST = ["mouseX", "mouseY"]
LOADING_MOVIE_STRING = "Loading movie data..."
UPDATE_INPUT_EDITOR_STRING = "Updating input editor..."
INPUT_EDITOR_UPDATED_STRING = "Input editor updated."
MOVIE_LOADED_STRING = "Movie file loaded."
EXIT_STRING = "GMReplay was closed."
INPUTS_STRING = "Inputs"
RAW_HIDE_STRING = "Raw (abridged)"
RAW_SHOW_STRING = "Raw (full)"
INPUT_RAW_LABEL = "Input display format:"
SAVE_MOVIE_STRING = "Saving movie file..."
SAVED_MOVIE_STRING = "Movie file saved."
SAVE_OPTION_STRING = "Save movie file"
SAVE_AS_OPTION_STRING = "Save movie file as..."
PREFERENCES_STRING = "Preferences"
MAX_HISTORY_STRING = "Maximum file history size:"
CLEAR_HISTORY_STRING = "Clear file history"
SUPPRESS_GAME_OUTPUT_STRING = "Suppress game debug output"
ABOUT_MESSAGE = (
    "GMReplay is a program for creating tool-assisted replays of Windows-based GameMaker games from GameMaker: Studio 1 or later.\n\n"
    + "To submit an issue, receive the most up-to-date versions, or contribute to the development of GMReplay, visit the Github repository at:"
)
ABOUT_LINK = "https://github.com/OceanBagel/GMReplay/"
SELECT_COLUMNS_TITLE_STRING = "Select columns to add"
SELECT_COLUMNS_STRING = "Select columns to add:"
INSERT_COLUMN_TEXT = "Insert columns"
ADDING_COLUMNS_STRING = "Adding columns "
OK_STRING = "Ok"

# Movie parsing strings
WHEEL_UP = "wheelUp"
WHEEL_DOWN = "wheelDown"
MOUSE_X = "mouseX"
MOUSE_Y = "mouseY"
TRUNCATED_DATA_STRING = "Warning: frame data was truncated. This may be due to invalid input."
INVALID_INPUT_STRING = "Invalid input. This cell accepts integer inputs only."

# Config strings
CONFIG_DATA_ERROR_STRING = "Error when loading config.ini: data error. Reloading default configuration."
CONFIG_FILE_NOT_FOUND_STRING = "Error when loading config.ini: file not found. Reloading default configuration."

# Other constants

# UI constants
GLOBAL_PADDING = 4
COLUMN_SMALL_WIDTH = 50
COLUMN_MEDIUM_WIDTH = 100
COLUMN_BIG_WIDTH = 150
COLUMN_VERYBIG_WIDTH = 250
COLUMN_MASSIVE_WIDTH = 1500
SHEET_BINDINGS = (
    "single_select",
    "drag_select",
    "select_all",
    "column_select",
    "row_select",
    "column_width_resize",
    "double_click_column_resize",
    "arrowkeys",
    "right_click_popup_menu",
    "rc_select",
    "rc_insert_row",
    "rc_delete_row",
    "copy",
    "cut",
    "paste",
    "delete",
    "undo",
)

# Movie parsing constants
VK_NAMES = {
    -3: "Mouse1",  # Mouse buttons will be put here too in values <0
    -2: "Mouse2",
    -1: "Mouse3",
    0: "",  # Represents no key
    8: "Backspace",  # Key name dict, doesn't need to match any specification, just needs to be human-readable
    9: "Tab",
    13: "Enter",
    # 16: "Shift", # These names should be stripped out because they always accompany the left/right versions
    # 17: "Control",
    # 18: "Alt",
    19: "Pause",
    20: "CapsLock",
    27: "Escape",
    32: "Space",
    33: "PageUp",
    34: "PageDown",
    35: "End",
    36: "Home",
    37: "ArrowLeft",
    38: "ArrowUp",
    39: "ArrowRight",
    40: "ArrowDown",
    44: "PrintScreen",
    45: "Insert",
    46: "Delete",
    48: "0",
    49: "1",
    50: "2",
    51: "3",
    52: "4",
    53: "5",
    54: "6",
    55: "7",
    56: "8",
    57: "9",
    65: "a",
    66: "b",
    67: "c",
    68: "d",
    69: "e",
    70: "f",
    71: "g",
    72: "h",
    73: "i",
    74: "j",
    75: "k",
    76: "l",
    77: "m",
    78: "n",
    79: "o",
    80: "p",
    81: "q",
    82: "r",
    83: "s",
    84: "t",
    85: "u",
    86: "v",
    87: "w",
    88: "x",
    89: "y",
    90: "z",
    91: "WindowsLeft",
    92: "WindowsRight",
    93: "ContextMenu",
    96: "Numpad0",
    97: "Numpad1",
    98: "Numpad2",
    99: "Numpad3",
    100: "Numpad4",
    101: "Numpad5",
    102: "Numpad6",
    103: "Numpad7",
    104: "Numpad8",
    105: "Numpad9",
    106: "NumpadMultiply",
    107: "NumpadAdd",
    108: "NumpadSeparator",
    109: "NumpadSubtract",
    110: "NumpadDecimal",
    111: "NumpadDivide",
    112: "F1",
    113: "F2",
    114: "F3",
    115: "F4",
    116: "F5",
    117: "F6",
    118: "F7",
    119: "F8",
    120: "F9",
    121: "F10",
    122: "F11",
    123: "F12",
    144: "NumLock",
    145: "ScrollLock",
    160: "ShiftLeft",
    161: "ShiftRight",
    162: "ControlLeft",
    163: "ControlRight",
    164: "AltLeft",
    165: "AltRight",
    173: "AudioVolumeMute",
    174: "AudioVolumeDown",
    175: "AudioVolumeUp",
    181: "LaunchMediaPlayer",
    182: "LaunchApplication1",
    183: "LaunchApplication2",
    186: "Semicolon",
    187: "Equal",
    188: "Comma",
    189: "Minus",
    190: "Period",
    191: "Slash",
    192: "Backquote",
    219: "BracketLeft",
    220: "Backslash",
    221: "BracketRight",
    222: "Quote",
}
KEYS_THAT_PRINT = {
    32: "Space",
    48: "0",
    49: "1",
    50: "2",
    51: "3",
    52: "4",
    53: "5",
    54: "6",
    55: "7",
    56: "8",
    57: "9",
    65: "a",
    66: "b",
    67: "c",
    68: "d",
    69: "e",
    70: "f",
    71: "g",
    72: "h",
    73: "i",
    74: "j",
    75: "k",
    76: "l",
    77: "m",
    78: "n",
    79: "o",
    80: "p",
    81: "q",
    82: "r",
    83: "s",
    84: "t",
    85: "u",
    86: "v",
    87: "w",
    88: "x",
    89: "y",
    90: "z",
    96: "0",
    97: "1",
    98: "2",
    99: "3",
    100: "4",
    101: "5",
    102: "6",
    103: "7",
    104: "8",
    105: "9",
    106: "*",
    107: "+",
    108: ",",
    109: "-",
    110: ".",
    111: "/",
    186: ";",
    187: "=",
    188: ",",
    189: "-",
    190: ".",
    191: "/",
    192: "`",
    219: "[",
    220: "\\",
    221: "]",
    222: "'",
}
