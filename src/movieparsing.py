# Built-in packages
import os

# Constants
import constants as c

# Local packages
from utils import keyName, listIndicesThatAreTrue


def loadMovie(pathToMovieFile):
    """
    Take a path to the movie file, return a list of frames, each frame containing a list of inputs

    Args:
        pathToMovieFile (str): File path to the movie file

    Returns:
        list: List of frames containing the raw inputs
    """

    loadedMovieData = []

    # Return a blank list if file doesn't exist. Probably a new filename for recording.
    if not os.path.isfile(pathToMovieFile):
        return loadedMovieData

    # File exists, load it for reading
    with open(pathToMovieFile, "rb") as fid:
        while len(fid.read(1)) == 1:
            # Check if there are bytes to read
            fid.seek(-1, 1)
            # Move the pointer back one byte after the read from the previous line

            # Catch any decoding errors, discard that frame's data, and break
            try:
                # Start parsing, should be a total of 3034 bytes of data
                lastChar = fid.read(2)
                lastChar = lastChar.decode("utf-16")

                inputString = ""
                for _ in range(1025):
                    inputString += fid.read(2).decode("utf-16")
                inputString.strip("\x00")

                lastKey = int.from_bytes(fid.read(4), "little")

                currentKey = int.from_bytes(fid.read(4), "little")

                keyDown = [False] * 256
                for i in range(256):
                    keyDown[i] = int.from_bytes(fid.read(1)) != 0
                keyDown = listIndicesThatAreTrue(keyDown)
                # This lists all indices where the corresponding elements are true

                keyReleased = [False] * 256
                for i in range(256):
                    keyReleased[i] = int.from_bytes(fid.read(1)) != 0
                keyReleased = listIndicesThatAreTrue(keyReleased)

                keyPressed = [False] * 256
                for i in range(256):
                    keyPressed[i] = int.from_bytes(fid.read(1)) != 0
                keyPressed = listIndicesThatAreTrue(keyPressed)

                lastButton = [0] * 10
                for i in range(10):
                    lastButton[i] = int.from_bytes(fid.read(4), "little")
                # It seems that only the first slot is used

                currentButton = [0] * 10
                for i in range(10):
                    currentButton[i] = int.from_bytes(fid.read(4), "little")
                # It seems that only the first slot is used

                buttonDown = [[0 for i in range(3)] for j in range(10)]
                for i in range(10):
                    for j in range(3):
                        buttonDown[i][j] = int.from_bytes(fid.read(1)) != 0
                    buttonDown[i] = [element + 1 for element in listIndicesThatAreTrue(buttonDown[i])]
                    # Add 1 to get to the mouse button. Needs to be subtracted back when decoding.
                # It seems that only the first slot is used

                buttonReleased = [[0 for i in range(3)] for j in range(10)]
                for i in range(10):
                    for j in range(3):
                        buttonReleased[i][j] = int.from_bytes(fid.read(1)) != 0
                    buttonReleased[i] = [element + 1 for element in listIndicesThatAreTrue(buttonReleased[i])]
                    # Add 1 to get to the mouse button. Needs to be subtracted back when decoding.
                # It seems that only the first slot is used

                buttonPressed = [[0 for i in range(3)] for j in range(10)]
                for i in range(10):
                    for j in range(3):
                        buttonPressed[i][j] = int.from_bytes(fid.read(1)) != 0
                    buttonPressed[i] = [element + 1 for element in listIndicesThatAreTrue(buttonPressed[i])]
                    # Add 1 to get to the mouse button. Needs to be subtracted back when decoding.
                # It seems that only the first slot is used

                wheelUp = [0] * 10
                for i in range(10):
                    wheelUp[i] = int.from_bytes(fid.read(1))
                # It seems that only the first slot is used

                wheelDown = [0] * 10
                for i in range(10):
                    wheelDown[i] = int.from_bytes(fid.read(1))
                # It seems that only the first slot is used

                mousePos = fid.read(8).hex()  # TODO: is this data actually used? GUI mouse position?

                mouseX = int.from_bytes(fid.read(4), "little")

                mouseY = int.from_bytes(fid.read(4), "little")

                thisFrameData = [
                    lastChar,
                    inputString,
                    lastKey,
                    currentKey,
                    keyDown,
                    keyReleased,
                    keyPressed,
                    lastButton,
                    currentButton,
                    buttonDown,
                    buttonReleased,
                    buttonPressed,
                    wheelUp,
                    wheelDown,
                    mousePos,
                    mouseX,
                    mouseY,
                ]

                loadedMovieData += [thisFrameData]

            except UnicodeDecodeError:
                print("Decode error. Final frame data was incomplete and has been discarded.")
                break

    return loadedMovieData


def recordingToInputs(loadedMovieData):
    """
    Take the movie data in recording format and convert it to input format, returning a list of column headers, a list of keycode numbers, and a list of input data

    Args:
        loadedMovieData (list): List of loaded movie data in raw format

    Returns:
        list, list, list: List of column headers, list of keycode numbers, list of input data. All three lists use the same order.
    """

    inputFormatMovieData = []
    inputKeycodeColumnLabels = []
    mouseUpPresent = False
    mouseDownPresent = False
    keyRowList = []
    rowList = []

    for row in loadedMovieData:
        thisKeyRow = []
        thisRow = []

        # Add the keypresses from keyDown
        # Strip out ctrl, alt, and shift. These have two keycodes and the left/right version is what will be displayed.
        thisKeyRow = [element for element in row[4] if element not in (16, 17, 18)]

        # Check to see if there are new keys to add
        for element in thisKeyRow:
            if element not in inputKeycodeColumnLabels:
                inputKeycodeColumnLabels += [element]
        # Add mouse button
        for element in row[9][0]:
            thisKeyRow += [-4 + element]
            # Stored as -3: mouse1, -2: mouse2, -1: mouse3. These correspond to index values 0, 1, 2 respectively.
            if -4 + element not in inputKeycodeColumnLabels:
                inputKeycodeColumnLabels += [-4 + element]
                # Make mouse buttons negative to distinguish them

        # Add wheelUp or wheelDown as strings
        if row[12][0] == 1:
            thisRow += [c.WHEEL_UP]
            mouseUpPresent = True
        else:
            thisRow += [""]
        if row[13][0] == 1:
            thisRow += [c.WHEEL_DOWN]
            mouseDownPresent = True
        else:
            thisRow += [""]
        # Add mouse coords as a pair [x, y]
        thisRow += [row[15]]
        thisRow += [row[16]]

        # Add this row to the lists
        keyRowList += [thisKeyRow]
        rowList += [thisRow]

    # Sort the input labels
    inputKeycodeColumnLabels.sort()

    # Now go through the inputs again to form the final rows
    for i in range(len(rowList)):
        thisRow = []

        # Check each column and either add the key name or a blank
        for element in inputKeycodeColumnLabels:
            if element in keyRowList[i]:
                thisRow += [keyName(element)]
            else:
                thisRow += [""]

        # Add mouse inputs
        if mouseUpPresent:
            thisRow += [rowList[i][0]]
        if mouseDownPresent:
            thisRow += [rowList[i][1]]
        thisRow += [rowList[i][2]]
        thisRow += [rowList[i][3]]

        # Add to the final list
        inputFormatMovieData += [thisRow]

    inputKeynameColumnLabels = [""] * len(inputKeycodeColumnLabels)
    # Convert the input column labels to names
    for i in range(len(inputKeycodeColumnLabels)):
        inputKeynameColumnLabels[i] = keyName(inputKeycodeColumnLabels[i])

    if mouseUpPresent:
        inputKeynameColumnLabels += [c.WHEEL_UP]
    if mouseDownPresent:
        inputKeynameColumnLabels += [c.WHEEL_DOWN]

    inputKeynameColumnLabels += [c.MOUSE_X, c.MOUSE_Y]

    return inputKeynameColumnLabels, inputKeycodeColumnLabels, inputFormatMovieData


def inputsToRecording(inputColumnsList, keyCodesList, inputFormatMovieData):
    """
    Takes the data from input format into raw recording format for saving

    Args:
        inputColumnsList (list): Column headers list
        keyCodesList (list): Key codes list
        inputFormatMovieData (list): Movie data list in input format

    Returns:
        list: Movie data in raw recording format
    """

    loadedMovieData = []
    prevKeyDown = []
    prevButtonDown = []
    prevLastKey = 0
    prevLastButton = 0
    for row in inputFormatMovieData:
        # Initialize each value in the frame
        lastChar = ""
        inputString = ""
        lastKey = 0
        currentKey = 0
        keyDown = []
        keyReleased = []
        keyPressed = []
        lastButton = [0 for j in range(10)]
        currentButton = [0 for j in range(10)]
        buttonDown = [[] for j in range(10)]
        buttonReleased = [[] for j in range(10)]
        buttonPressed = [[] for j in range(10)]
        keyButtonDown = []
        wheelUp = [0 for j in range(10)]
        wheelDown = [0 for j in range(10)]
        mousePos = 0
        mouseX = 0
        mouseY = 0

        # Start with the keypresses/button presses, separate them later
        for index in range(len(keyCodesList)):
            # Convert from names to numbers
            thisElement = next(key for key, value in c.VK_NAMES.items() if value == row[index])
            if thisElement != 0:
                if thisElement in (160, 161):  # Shift
                    keyButtonDown += [16]
                elif thisElement in (162, 163):  # Ctrl
                    keyButtonDown += [17]
                elif thisElement in (164, 165):  # Alt
                    keyButtonDown += [18]
                keyButtonDown += [thisElement]

        # Now look at the key history variables
        # keyPressed/buttonPressed and separate them here
        if len(keyButtonDown) > 0:
            for key in keyButtonDown:
                if key > 0:  # is a key
                    if key not in prevKeyDown:
                        # Pressed
                        keyPressed += [key]
                    keyDown += [key]
                if key < 0:  # is a button
                    if key + 4 not in prevButtonDown:
                        # Pressed, add 4 to convert to mouse button
                        buttonPressed[0] += [key + 4]
                    buttonDown[0] += [key + 4]

        # keyReleased
        if len(prevKeyDown) > 0:
            for key in prevKeyDown:
                if key not in keyDown:
                    keyReleased += [key]

        # buttonReleased
        if len(prevButtonDown) > 0:
            for button in prevButtonDown:
                if button not in buttonDown:
                    buttonReleased[0] += [button]

        # lastKey/button and currentkey/button
        if len(keyPressed) > 0:
            # Check if the last key isn't a button
            if keyPressed[-1] > 0:
                # currentKey
                for key in keyDown:
                    if key in keyPressed and key not in keyReleased and key > 0:
                        currentKey = key
                # lastKey
                lastKey = keyPressed[-1]
                # Pick the last one in the list. This may be inaccurate if order matters.
                prevLastKey = lastKey
            else:
                # No keys this frame
                lastKey = prevLastKey
                currentKey = 0
            # Check if the first key is a button
            if keyPressed[0] < 0:
                lastButton[0] = keyPressed[0]
                prevLastButton = lastButton[0]
            else:
                # No buttons this frame
                lastButton[0] = prevLastButton
                currentButton[0] = 0
        else:
            # No keys or buttons this frame
            lastKey = prevLastKey
            lastButton[0] = prevLastButton
            currentKey = 0
            currentButton[0] = 0

        # lastChar
        lastChar = chr(lastKey) if lastKey in c.KEYS_THAT_PRINT else ""

        # inputString
        # (This would normally use capslock/shift to include the correct keys, as well as system-dependent key repetition and allows multiple of the same key in one frame)
        # (Basically, it's impossible to recreate based on inputs alone, so we do our best and rely on the user manually adding the correct string if required)
        # TODO: Allow the user to manually add the correct string.
        for key in keyDown:
            if key > 0 and key in c.KEYS_THAT_PRINT:
                inputString += c.KEYS_THAT_PRINT[key]
            if key == 8:  # Backspace
                inputString = inputString[:-1]
        inputString = inputString[:1024]
        # Trim it to 1024 characters in length

        # mauswheel
        # Check for wheel up in the keyname column labels, which is the keycode column labels plus mousewheel and mouse position
        if c.WHEEL_UP in inputColumnsList:
            # If it exists, check if it's activated this frame
            if c.WHEEL_UP in row[inputColumnsList.index(c.WHEEL_UP)]:
                # If it is, add the press
                wheelUp[0] = 1
            else:
                wheelUp[0] = 0
        else:
            wheelUp[0] = 0

        # Now do wheelDown
        if c.WHEEL_DOWN in inputColumnsList:
            # If it exists, check if it's activated this frame
            if c.WHEEL_DOWN in row[inputColumnsList.index(c.WHEEL_DOWN)]:
                # If it is, add the press
                wheelDown[0] = 1
            else:
                wheelDown[0] = 0
        else:
            wheelDown[0] = 0

        # Mouse position
        # mouseX and mouseY
        mouseX = row[-2]
        mouseY = row[-1]

        # mousePos, just set to 0 for now
        mousePos = bytes(8).hex()

        # Put the inputs together and add it to the data
        thisFrameData = [
            lastChar,
            inputString,
            lastKey,
            currentKey,
            keyDown,
            keyReleased,
            keyPressed,
            lastButton,
            currentButton,
            buttonDown,
            buttonReleased,
            buttonPressed,
            wheelUp,
            wheelDown,
            mousePos,
            mouseX,
            mouseY,
        ]

        loadedMovieData += [thisFrameData]

    return loadedMovieData


def saveMovie(pathToMovieFile, loadedMovieData):
    """
    Take a path to the movie file and the loaded data from loadMovie(), and save the data into the movie file, overwriting the file

    Args:
        pathToMovieFile (str): Path to the location where the movie file should be saved
        loadedMovieData (list): Loaded movie data in raw recording format
    """

    # First open the file for binary writing
    with open(pathToMovieFile, "wb") as fid:
        # Now iterate over each frame
        for frame in loadedMovieData:
            frameBytes = b""

            # Start converting from loaded format to bytes
            # lastChar
            size = 2
            bytesToAdd = frame[0].encode("utf-16le")  # 2 bytes
            if len(bytesToAdd) > size:
                print(c.TRUNCATED_DATA_STRING)
                bytesToAdd = bytesToAdd[:size]
            if len(bytesToAdd) < size:
                bytesToAdd = bytesToAdd + bytes(size - len(bytesToAdd))
            frameBytes += bytesToAdd

            # inputString
            size = 2050
            # 1025*2 because each char is 2 bytes
            bytesToAdd = frame[1].encode("utf-16le")
            # Max 2050 bytes
            if len(bytesToAdd) > size:
                print(c.TRUNCATED_DATA_STRING)
                bytesToAdd = bytesToAdd[:size]
            if len(bytesToAdd) < size:
                bytesToAdd = bytesToAdd + bytes(size - len(bytesToAdd))
            frameBytes += bytesToAdd

            # lastKey
            size = 4
            bytesToAdd = frame[2].to_bytes(size, "little")
            frameBytes += bytesToAdd

            # currentKey
            size = 4
            bytesToAdd = frame[3].to_bytes(size, "little")
            frameBytes += bytesToAdd

            # keyDown
            bytesToAdd = bytearray(256)
            for element in frame[4]:
                bytesToAdd[element] = 1
                # Sets to b'\x01'
            bytesToAdd = bytes(bytesToAdd)
            frameBytes += bytesToAdd

            # keyReleased
            bytesToAdd = bytearray(256)
            for element in frame[5]:
                bytesToAdd[element] = 1
                # Sets to b'\x01'
            bytesToAdd = bytes(bytesToAdd)
            frameBytes += bytesToAdd

            # keyPressed
            bytesToAdd = bytearray(256)
            for element in frame[6]:
                bytesToAdd[element] = 1
                # Sets to b'\x01'
            bytesToAdd = bytes(bytesToAdd)
            frameBytes += bytesToAdd

            # lastButton
            size = 4
            for element in frame[7]:
                # always 10 elements
                bytesToAdd = (element).to_bytes(size, "little")
                frameBytes += bytesToAdd

            # currentButton
            size = 4
            for element in frame[8]:
                # always 10 elements
                bytesToAdd = (element).to_bytes(size, "little")
                frameBytes += bytesToAdd

            # buttonDown
            for element in frame[9]:
                # 10 elements
                bytesToAdd = bytearray(3)
                for subelement in element:
                    bytesToAdd[subelement - 1] = 1
                    # Sets to b'\x01', subtracted 1 because 1 was added before
                bytesToAdd = bytes(bytesToAdd)
                frameBytes += bytesToAdd

            # buttonReleased
            for element in frame[10]:
                # 10 elements
                bytesToAdd = bytearray(3)
                for subelement in element:
                    bytesToAdd[subelement - 1] = 1
                    # Sets to b'\x01', subtracted 1 because 1 was added before
                bytesToAdd = bytes(bytesToAdd)
                frameBytes += bytesToAdd

            # buttonPressed
            for element in frame[11]:
                # 10 elements
                bytesToAdd = bytearray(3)
                for subelement in element:
                    bytesToAdd[subelement - 1] = 1
                    # Sets to b'\x01', subtracted 1 because 1 was added before
                bytesToAdd = bytes(bytesToAdd)
                frameBytes += bytesToAdd

            # wheelUp
            size = 1
            for element in frame[12]:
                # always 10 elements
                bytesToAdd = element.to_bytes(size, "little")
                frameBytes += bytesToAdd

            # wheelDown
            size = 1
            for element in frame[13]:
                # always 10 elements
                bytesToAdd = element.to_bytes(size, "little")
                frameBytes += bytesToAdd

            # mousePos
            bytesToAdd = bytes.fromhex(frame[14])
            # 8 bytes
            frameBytes += bytesToAdd

            # mouseX
            size = 4
            bytesToAdd = frame[15].to_bytes(size, "little")
            frameBytes += bytesToAdd

            # mouseY
            size = 4
            bytesToAdd = frame[16].to_bytes(size, "little")
            frameBytes += bytesToAdd

            # Write this frame's bytes
            fid.write(frameBytes)
