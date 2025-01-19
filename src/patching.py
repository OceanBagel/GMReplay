# Built-in packages
import re

# Constants
import constants as c

# Local packages
from utils import check32BitOr64Bit, intToBytes


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

    bitness = check32BitOr64Bit(exeData)

    if bitness == 32:
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
    elif bitness == 64:
        # Search for the mouse input offsets
        mousePattern1 = b"\x48\x8d.{4}\x00\xba\x04\x00\x00\x00\x44\x8d\x42\xfd.{12}\xba\x04\x00\x00\x00\x44\x8d\x42\xfd\x48\x8d.{4}\x00"
        # Pattern 2 is for the playback read of the mouse inputs
        mousePattern2 = b"\x48\x8d.{4}\x00\xba\x04\x00\x00\x00\x44\x8d\x42\xfd.{12}\xba\x04\x00\x00\x00\x48\x8d.{4}\x00"
        mouseRegex = re.compile(mousePattern1)

        # Run the regex search. One match expected.
        mouseOffsets = []
        g_MouseX_LEA_offset = [0] * 4
        g_MouseY_LEA_offset = [0] * 4
        g_MouseX_rel_offset = [0] * 4
        g_MouseY_rel_offset = [0] * 4
        g_MouseX_new_rel_offset = [0] * 4
        g_MouseY_new_rel_offset = [0] * 4

        for match_obj in mouseRegex.finditer(exeData):
            mouseOffsets += [match_obj.start()]

        mouseRegex = re.compile(mousePattern2)
        for match_obj in mouseRegex.finditer(exeData):
            mouseOffsets += [match_obj.start()]

        # if it's not 2 after we ran the check
        if len(mouseOffsets) != 4:
            print(mouseOffsets)
            print(c.PATCH_MOUSE_FAIL_STRING)

        # Keep going if there is no issue, otherwise skip ahead to the next patch
        else:
            # If there are exactly two matches, we have g_MouseX and g_MouseY offsets and values
            for i in range(4):
                g_MouseX_LEA_offset[i] = mouseOffsets[i]
                g_MouseY_LEA_offset[i] = mouseOffsets[i] + 37
                if i > 1:
                    g_MouseY_LEA_offset[i] -= 4

                # Get the relative addresses
                g_MouseX_rel_offset[i] = int.from_bytes(
                    exeData[g_MouseX_LEA_offset[i] + 3 : g_MouseX_LEA_offset[i] + 7][::-1]
                )
                g_MouseY_rel_offset[i] = int.from_bytes(
                    exeData[g_MouseY_LEA_offset[i] + 3 : g_MouseY_LEA_offset[i] + 7][::-1]
                )

            # Get the absolute offsets
            g_MouseX_abs_offset = g_MouseX_rel_offset[0] + g_MouseX_LEA_offset[0] + 7 - 0xC00
            g_MouseY_abs_offset = g_MouseY_rel_offset[0] + g_MouseY_LEA_offset[0] + 7 - 0xC00

            # Small sanity check
            if g_MouseX_abs_offset != g_MouseX_rel_offset[1] + g_MouseX_LEA_offset[1] + 7 - 0xC00:
                print(c.MOUSE_OFFSET_MISMATCH)

            # Next we search for the next reference to g_MouseX_abs_offset which should be an 89 call
            mouseMOVPattern = b"\x89.{4}\x00"
            mouseMOVRegex = re.compile(mouseMOVPattern)
            matchFound = False
            for match in mouseMOVRegex.finditer(exeData):
                # Test the match. For each match, add ccbbaa to the offset of the value +7 from the beginning of the search term and check against the target value.
                if (
                    int.from_bytes(exeData[match.start() + 2 : match.start() + 6][::-1]) + match.start() + 6 - 0xC00
                    == g_MouseX_abs_offset
                ):
                    matchFound = True
                    # This is the next match that we're looking for. Record the mousePosX and MousePosY absolute addresses.
                    g_MousePosX_MOV_offset = match.start() - 18
                    g_MousePosY_MOV_offset = match.start() - 12

                    g_MousePosX_rel_offset = int.from_bytes(
                        exeData[g_MousePosX_MOV_offset + 2 : g_MousePosX_MOV_offset + 6][::-1]
                    )
                    g_MousePosY_rel_offset = int.from_bytes(
                        exeData[g_MousePosY_MOV_offset + 2 : g_MousePosY_MOV_offset + 6][::-1]
                    )

                    g_MousePosX_abs_offset = g_MousePosX_rel_offset + g_MousePosX_MOV_offset + 6 - 0xC00
                    g_MousePosY_abs_offset = g_MousePosY_rel_offset + g_MousePosY_MOV_offset + 6 - 0xC00

                    break

            if not matchFound:
                print(c.PATCH_MOUSE_FAIL_STRING)

            else:
                # Now take the difference between Mouse and MousePos
                mouseXOffsetDiff = g_MousePosX_abs_offset - g_MouseX_abs_offset
                mouseYOffsetDiff = g_MousePosY_abs_offset - g_MouseY_abs_offset

                # Add these to the X/Y relative offsets
                for i in range(4):
                    g_MouseX_new_rel_offset[i] = g_MouseX_rel_offset[i] + mouseXOffsetDiff
                    g_MouseY_new_rel_offset[i] = g_MouseY_rel_offset[i] + mouseYOffsetDiff

                    # Overwrite the offsets in the new data
                    newExeData[g_MouseX_LEA_offset[i] + 3 : g_MouseX_LEA_offset[i] + 6] = intToBytes(
                        g_MouseX_new_rel_offset[i]
                    )[::-1]
                    newExeData[g_MouseY_LEA_offset[i] + 3 : g_MouseY_LEA_offset[i] + 6] = intToBytes(
                        g_MouseY_new_rel_offset[i]
                    )[::-1]

                exeModified = True
                print(c.PATCH_MOUSE_SUCCESS_STRING)

    else:
        print(c.PATCH_MOUSE_FAIL_STRING)

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

    # Determine the bitness
    bitness = check32BitOr64Bit(exeData)

    # Find the magic word representing the start of the image optional header
    # It should be at the beginning, otherwise oopsies
    if bitness == 32:
        imgOptHeadrAddr = exeData.find(b"\x0b\x01", 0x0, 0x200)
    elif bitness == 64:
        imgOptHeadrAddr = exeData.find(b"\x0b\x02", 0x0, 0x200)
    else:
        print(failureMessage)
        return newExeData, exeModified

    # If it does equal -1, that's a failure and we'll kick back out to the warning below
    if imgOptHeadrAddr != -1:
        # The image optional header is different between 32-bit and 64-bit, so the data pointer offset is calculated differently
        if bitness == 32:
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

        # We already checked for bitness failure so no need to do so again
        else:  # bitness == 64
            # Find string reference LEA call
            funcLEAPattern = b"\x48\x8d.{4}\x00"
            funcLEARegex = re.compile(funcLEAPattern)
            for match in funcLEARegex.finditer(exeData):
                # Test the match. For each match, add ccbbaa to the offset of the value +7 from the beginning of the search term and check against the target value.
                if (
                    int.from_bytes(exeData[match.start() + 3 : match.start() + 7][::-1]) + match.start() + 7 - 0xC00
                    == sourceStringOffset
                ):
                    # The function definitions are 7 bytes earlier
                    sourceFuncDefOffset = match.start() - 7
                    if destFuncDefOffset != -1:
                        break
                elif (
                    int.from_bytes(exeData[match.start() + 3 : match.start() + 7][::-1]) + match.start() + 7 - 0xC00
                    == destStringOffset
                ):
                    # The function definitions are 7 bytes earlier
                    destFuncDefOffset = match.start() - 7
                    if sourceFuncDefOffset != -1:
                        break

    if imgOptHeadrAddr == -1 or destFuncDefOffset == -1 or sourceFuncDefOffset == -1:
        # We couldn't do the patch
        print(failureMessage)
        return newExeData, exeModified

    if bitness == 32:
        # The function itself starts 4 bytes earlier
        sourceFunction = exeData[sourceFuncDefOffset - 4 : sourceFuncDefOffset]

        # Overwrite the function
        newExeData[destFuncDefOffset - 4 : destFuncDefOffset] = sourceFunction
        exeModified = True
    else:  # bitness == 64
        # Record the relative offsets and translate them to absolute offsets to the function calls
        sourceFuncRelOffset = int.from_bytes(exeData[sourceFuncDefOffset + 3 : sourceFuncDefOffset + 7][::-1])
        sourceFuncAbsOffset = sourceFuncRelOffset + sourceFuncDefOffset + 7 - 0xC00

        # Calculate the relative dest function offset using the absolute location of the source function
        destFuncDefNewOffset = sourceFuncAbsOffset - destFuncDefOffset + 7 + 0xC00

        # Overwrite the data
        newExeData[destFuncDefOffset + 3 : destFuncDefOffset + 7] = intToBytes(destFuncDefNewOffset)[::-1]
        exeModified = True

    print(successMessage)
    return newExeData, exeModified
