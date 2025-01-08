# ![gmreplay_logo_24](https://github.com/user-attachments/assets/0cae9c64-ad0f-445a-a3f2-932f8ca2ff1e) GMReplay
## A program for creating tool-assisted replays of Windows-based GameMaker games from GameMaker: Studio 1 or later.

![image](https://github.com/user-attachments/assets/bfd76eea-b1bd-4848-9dc0-cfc50bd8ab8b)

GMReplay is a program for creating tool-assisted replays of Windows GameMaker games, intended for games that cannot be run on Linux. For GameMaker games that have native Linux versions or VM GameMaker games that can be ported to Linux, check out [libTAS](https://github.com/clementgallet/libTAS).

GMReplay relies on the built-in playback and recording features present in GameMaker games for frame-accurate input playback regardless of the Windows timing inaccuracies that otherwise cause difficulty with building conventional TAS tools for Windows games.

GMReplay is currently in development. See the below roadmap for future plans.

## Roadmap
**Phase 1 - Minimum implementation (Complete)**
- [X] Realtime recording and playback
- [X] Interactive command-line interface
- [X] Support for keyboard_check_direct and mouse inputs
- [X] Patch out randomize() for deterministic RNG

**Phase 2 - Piano roll interface (In testing)**
- [X] Graphical user interface
- [X] Piano roll interface for reading/writing inputs
- [X] Replay file parsing
- [X] Replay file writing/modification

**Phase 3 - Function hooking (Not started)**
- [ ] randomize hooking
- [ ] keyboard_check_direct hooking
- [ ] Mouse controls via function hooking
- [ ] Switch between recording and playback

**Phase 4 - Game loop hooking (Not started)**
- [ ] Frame advance
- [ ] Fast forward
- [ ] Time-based rng seeding

**Phase 5 - Tool-assisted replay minimum feature set from [TASVideos](https://tasvideos.org/Emulatorresources/Requirements) (Not started)**
- [ ] Savestates
- [ ] Encoding
- [ ] Time measurement
- [ ] Rerecord count
- [ ] Audio hooking and sync

**Phase 6 - Functional parity with libTAS (Not started)**
- [ ] Annotations/authors/subtitles
- [ ] System time modification
- [ ] On-screen display of inputs, frames, etc.

## How to install

There are a couple different ways to install GMReplay.

### Release version (recommended)

The latest release is the recommended way to run GMReplay. From the Github page, click on "Releases" on the right, find the latest version, and download "GMReplay.exe". There is no additional installation process, so you can run GMReplay.exe directly to use GMReplay.

### Python environment

To run GMReplay in your own Python environment, you first need to install Python 3.12 or higher.

GMReplay currently uses the following built-in Python packages:
- sys
- os
- re
- functools
- itertools
- subprocess
- tkinter
- webbrowser
- traceback
- configparser
- dataclasses

GMReplay also requires the following package, installable through pip:
- tksheet
- dacite

Once you have Python and the required packages installed, download the src folder and run gmreplay.py. This will open GMReplay's graphical user interface (GUI), as well as a console where status notifications will be printed.

## How to use

Because this is in early development, it may not be feature-complete or user-friendly yet.

In the GUI, GMReplay will prompt you to choose the exe file for the game (GameMaker Studio 1 games or later), the data.win (if applicable), and the .gmr replay file.

Once your selections have been made, GMReplay will attempt to create a patched version of the exe file. This is stored separately from the exe file you selected. The patch enables mouse inputs, fixes an issue with certain keyboard functions, and forces deterministic RNG.

You can select either Recording or Playback, and then press Start to open the game in either recording or playback mode. There are currently no speed controls, so the recordings are all done in realtime.

The .gmr file automatically saves while the game's running in recording mode. To end recording, close the game or press the "Stop" button.

Once the .gmr movie file contains inputs, the inputs will be displayed in the GUI. From there, you can make edits by clicking individual cells, clicking and dragging to paint cells, or shift-clicking to paint a region of cells. You can add or delete rows by right clicking the row labels, and you can add columns by right clicking the column labels.

The movie file is saved automatically when you start playback. To save manually, go to "File" and then either "Save movie" or "Save movie as...".

## Issues

If you encounter any issues, please submit an issue on Github with the **game's name and version**, **GMReplay's version**, and **steps to reproduce** the issue.
