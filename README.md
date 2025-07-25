# Mossiicii Player

Mossiicii Player is a Python-based desktop music player built using PyQt5 and pygame. It supports MP3 playback, album art display, and voice command features. The player features a clean GUI with image-based custom buttons for all controls and supports automatic metadata and album art extraction using mutagen.

**Features**

  - Custom PyQt5 GUI with image-based control buttons
  - MP3 playback using pygame mixer
  - Displays album art using mutagen and PIL
  - Speech recognition support for basic commands
  - Play, Pause, Resume, Stop, Next, Previous controls
  - Volume control and track duration display
  - Dynamic album art rendering as circular thumbnails

**Technologies Used**

  - Python
  - PyQt5
  - pygame
  - mutagen
  - PIL (Pillow)
  - speech_recognition
  - threading, os, glob

**Requirements**

Install the required libraries:

    pip install PyQt5 pygame mutagen Pillow SpeechRecognition

Make sure you have `ffmpeg` installed if speech recognition uses microphone input.

**Run the App**

    python mossiicii_player.py

**Folder Structure (Suggested)**

    ├── mossiicii_player.py
    ├── assets/
    │   ├── play.png
    │   ├── pause.png
    │   ├── stop.png
    │   ├── next.png
    │   ├── prev.png
    │   └── volume.png
    └── music/
        ├── song1.mp3
        └── song2.mp3

**Future Improvements**

  - Add playlist saving and loading support
  - Include a seek bar for track progress
  - Add shuffle and repeat functionality
  - Voice feedback (text-to-speech)
  - Theme customization (dark/light)

