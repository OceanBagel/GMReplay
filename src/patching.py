# Built-in packages
import re

# Constants
import constants as c

# Local packages
from utils import intToBytes


def genPatchedExe(exePath, patchedName=c.PATCH_FILE_NAME):
    """
    Apply patches to the chosen exe and save it into the current working directory. Returns a path to the patched exe.

    Args:
        exePath (str): Path to the exe file to patch
        patchedName (str, optional): File name for the patched file. Defaults to c.PATCH_FILE_NAME.

    Returns:
        str: A path to the patched file (if successful) or a path to the original exe (if unsuccessful)
    """

    print(c.PATCH_START_STRING)  # "Patching mouse inputs..."

    exeModified = False

    # Read the exe into memory
    with open(exePath, "rb") as fid:
        exeData = fid.read()

    # Mutable version to write the patched exe
    newExeData = bytearray(exeData)

    # Search for the mouse input offsets
    mousePattern1 = b"\x6a\x01\x6a\x04\x68.{18}\x6a\x01\x6a\x04\x68"
    mousePattern2 = b"\x6a\x01\x6a\x04\x68.{19}\x6a\x01\x6a\x04\x68"
    patternOffset = 0
    mouseRegex = re.compile(mousePattern1)

    # Run the regex search. Two matches expected.
    mouseOffsets = []
    for match_obj in mouseRegex.finditer(exeData):
        mouseOffsets += [match_obj.start()]

    # Check against pattern 2
    if len(mouseOffsets) == 1:
        patternOffset = 1
        mouseRegex = re.compile(mousePattern2)
        for match_obj in mouseRegex.finditer(exeData):
            mouseOffsets += [match_obj.start()]

    # if it's still not 2 after we ran the second check
    if len(mouseOffsets) != 2:
        print(c.PATCH_MOUSE_FAIL_STRING)

    # Keep going if there is no issue, otherwise skip ahead to the next patch
    else:
        # If there are exactly two matches, we have g_MouseX and g_MouseY offsets and values
        g_MouseX_offsets = 2 * [0]
        g_MouseY_offsets = 2 * [0]

        g_MouseX_offsets[0] = mouseOffsets[0] + 5
        g_MouseX_offsets[1] = mouseOffsets[1] + 5

        g_MouseY_offsets[0] = mouseOffsets[0] + 28
        g_MouseY_offsets[1] = mouseOffsets[1] + 28 + patternOffset

        g_MouseX = exeData[g_MouseX_offsets[0] : g_MouseX_offsets[0] + 4]
        g_MouseY = exeData[g_MouseY_offsets[0] : g_MouseY_offsets[0] + 4]

        # Next we search forward past g_MouseY_offsets[1] to find the last pattern for g_MouseX
        mouseXUpdateOffset = exeData.find(g_MouseX, max(g_MouseY_offsets[0], g_MouseY_offsets[1]))
        # it could also be before mouseX on older versions
        mouseYUpdateOffset = exeData.find(g_MouseY, mouseXUpdateOffset - 64)

        # Take the last bytes of g_MouseX/Y for search terms
        g_MousePosX_offset = exeData.rfind(g_MouseX[-1], mouseXUpdateOffset - 8, mouseXUpdateOffset) - 3
        g_MousePosY_offset = exeData.rfind(g_MouseY[-1], mouseYUpdateOffset - 8, mouseYUpdateOffset) - 3

        # We now have g_MousePosX/Y
        g_MousePosX = exeData[g_MousePosX_offset : g_MousePosX_offset + 4]
        g_MousePosY = exeData[g_MousePosY_offset : g_MousePosY_offset + 4]

        # Finally, we overwrite g_MouseX/Y with g_MousePosX/Y
        newExeData[g_MouseX_offsets[0] : g_MouseX_offsets[0] + 4] = g_MousePosX
        newExeData[g_MouseX_offsets[1] : g_MouseX_offsets[1] + 4] = g_MousePosX
        newExeData[g_MouseY_offsets[0] : g_MouseY_offsets[0] + 4] = g_MousePosY
        newExeData[g_MouseY_offsets[1] : g_MouseY_offsets[1] + 4] = g_MousePosY
        exeModified = True
        print(c.PATCH_MOUSE_SUCCESS_STRING)

    print(c.PATCH_KEYDIRECT_STRING)

    # Patch keyboard_check_direct next
    newExeData, exeModified = replaceFunction(
        exeData,
        "keyboard_check",
        "keyboard_check_direct",
        newExeData,
        c.PATCH_KEYDIRECT_FAIL_STRING,
        c.PATCH_KEYDIRECT_SUCCESS_STRING,
        exeModified,
    )

    print(c.PATCH_RANDOMIZE_STRING)

    # Patch randomize
    newExeData, exeModified = replaceFunction(
        exeData,
        "random_get_seed",
        "randomize",
        newExeData,
        c.PATCH_RANDOMIZE_FAIL_STRING,
        c.PATCH_RANDOMIZE_SUCCESS_STRING,
        exeModified,
    )

    # Done with the patched exe, now write it to the working directory
    print(c.PATCH_SUCCESS_STRING)
    if exeModified is True:
        with open(patchedName, "wb") as fid:
            fid.write(newExeData)
        return patchedName

    else:
        return exePath


def replaceFunction(
    exeData,
    sourceFuncName,
    destFuncName,
    newExeData,
    failureMessage,
    successMessage,
    exeModified,
):
    """
    Replaces one function by overwriting its definition with another function

    Args:
        exeData (bytes): Loaded binary file representing the original exe, which is to remain unmodified
        sourceFuncName (str): The name of the source function to copy from
        destFuncName (str): The name of the destination function to be overwritten
        newExeData (bytes): Bytes representing the patched exe, which may have been previously modified in-place
        failureMessage (str): Message to print if patch fails
        successMessage (str): Message to print if patch is successful
        exeModified (boolean): Whether the exe was previously modified

    Returns:
        bool: Returns True if exeModified was True OR if the patch was done successfully.
              Returns False if exeModified was False AND the patch was not done successfully.
    """

    # Find the offsets to the string names
    destStringOffset = exeData.find(bytes(destFuncName, "utf-8") + b"\x00")
    sourceStringOffset = exeData.find(bytes(sourceFuncName, "utf-8") + b"\x00")

    destFuncDefOffset = -1
    sourceFuncDefOffset = -1

    # Find the magic word representing the start of the image optional header
    # It should be at the beginning, otherwise oopsies
    imgOptHeadrAddr = exeData.find(b"\x0b\x01", 0x0, 0x200)

    # If it does equal -1, that's a failure and we'll kick back out to the warning below
    if imgOptHeadrAddr != -1:
        baseOfDataAddr = imgOptHeadrAddr + 0x18
        # Reverse it and interpret it as an int
        baseOfData = int.from_bytes(exeData[baseOfDataAddr : baseOfDataAddr + 4][::-1])

        imageBaseAddr = imgOptHeadrAddr + 0x1C
        # Reverse it and interpret it as an int
        imageBase = int.from_bytes(exeData[imageBaseAddr : imageBaseAddr + 4][::-1])

        # The baseOfData represents the offset in the file to the data section, but it overshoots (due to padding?)
        # So we need to find the true start addr of the data section and record the difference
        padLength = 0x60
        dataStartAddr = exeData.rfind(bytes(padLength), 0, baseOfData) + padLength
        dataBaseDiff = baseOfData - dataStartAddr

        # The total pointer offset is the sum of this difference and the image base address
        dataPtrOffset = dataBaseDiff + imageBase

        # Now we have what we need to find the function definitions
        destFuncDefOffset = exeData.find(b"\x68" + intToBytes(destStringOffset + dataPtrOffset)[::-1])
        sourceFuncDefOffset = exeData.find(b"\x68" + intToBytes(sourceStringOffset + dataPtrOffset)[::-1])

    if imgOptHeadrAddr == -1 or destFuncDefOffset == -1 or sourceFuncDefOffset == -1:  # We couldn't do the patch
        print(failureMessage)
        return newExeData, exeModified

    # The function itself starts 4 bytes earlier
    sourceFunction = exeData[sourceFuncDefOffset - 4 : sourceFuncDefOffset]

    # Overwrite the function
    newExeData[destFuncDefOffset - 4 : destFuncDefOffset] = sourceFunction
    exeModified = True

    print(successMessage)
    return newExeData, exeModified
