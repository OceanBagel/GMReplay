# Built-in packages
import re
import webbrowser
from functools import reduce

# Local packages
import constants as c


def folder(filePath):
    """
    Returns the folder that contains the given file

    Args:
        filePath (str): Path to the file

    Returns:
        str: Path to the containing folder
    """

    return "/".join(re.split(r"/|\\", filePath)[:-1])  # get stickbugged lol


def intToBytes(integer):
    """
    Returns the bytes representation of a positive integer

    Args:
        integer (int): Positive integer to convert to bytes representation

    Returns:
        bytes: bytes representation of the input integer
    """

    if integer < 0:
        return b"\x00"

    hexStr = hex(integer).removeprefix("0x")
    hexStr = hexStr.zfill(len(hexStr) + len(hexStr) % 2)

    return bytes.fromhex(hexStr)


def rotate2DArray(array):
    """
    Rotates the 2d array, e.g. [[1, 2], [3, 4]] -> [[1, 3], [2, 4]]

    Args:
        array (list[list]): 2D list to rotate

    Returns:
        list[list]: Rotated 2d list
    """

    return list(list(thisTuple) for thisTuple in zip(*array[::], strict=False))


def reduceBitwiseOr(array):
    """
    Takes a 2+d array and returns which subarrays have any nonzero bytes in them, e.g. [[b'\x00', b'\x01'], [b'\x00', b'\x00']] -> [True, False]

    Args:
        array (list): Input list

    Returns:
        list[bool]: A list of booleans representing which subarrays had nonzero bytes
    """
    # Operate recursively on any subarrays
    if isinstance(array, list | tuple):
        return [bool(reduce(lambda x, y: x | y, reduceBitwiseOr(subarray), 0)) for subarray in array]
    # Make it not a string if it's a string
    elif isinstance(array, str):
        return [0] if array.strip().strip("\x00").strip("0") == "" else [1]
    # Make it not a string if it's a string
    elif isinstance(array, bytes):
        return [0] if array.strip(b"\x00") == b"" else [1]
    # Return single-element array if not an array
    else:
        return [array]


def trimOrPadList(array, length, padValue=None):
    """
    Trims or pads an input list to length by adding padvalue or slicing the list

    Args:
        array (list): Input list
        length (int): Target length
        padValue (Any, optional): Value to pad the list with if needed. Defaults to None.

    Returns:
        list: The trimmed or padded list of the desired length.
    """
    if len(array) < length:
        return array + [padValue] * (length - len(array))
    else:
        return array[:length]


def listIndicesThatAreTrue(array):
    """
    Returns a list of indices corresponding to elements that evaluate to true

    Args:
        array (list): Input list

    Returns:
        list: List of integers representing indices that evaluate to true
    """

    return [index for index, element in enumerate(array) if element]


def keyName(keycode):
    """
    Returns the name corresponding to a given key code, or the keycode itself if the key is not present in the dict

    Args:
        keycode (int): Input keycode

    Returns:
        str: Keyname
    """

    return c.VK_NAMES.get(keycode, keycode)


def keyCodes(keyname):
    """
    Returns the key code corresponding to a given key name

    Args:
        keyname (str): Input keyname

    Returns:
        int: Keycode
    """
    return next(key for key, value in c.VK_NAMES.items() if value == keyname)


def stringify(twoDimList):
    """
    Takes a 2d list and turns each sub-sub-element into a string, returning a new list

    Args:
        twoDimList (list[list]): Input 2d list

    Returns:
        list[list[str]]: Output 2d list where the sub-sub-elements are strings
    """

    stringified2dList = []
    for row in twoDimList:
        thisRow = []
        for element in row:
            thisRow += [str(element)]
        stringified2dList += [thisRow]
    return stringified2dList


def openURL(url):
    """
    Opens the given url in the default browser

    Args:
        url (str): URL to open
    """
    webbrowser.open_new_tab(url)
