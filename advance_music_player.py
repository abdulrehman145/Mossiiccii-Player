import os
import sys
import glob
import pygame
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5.QtGui import QIcon, QFont, QPixmap, QImage
from PyQt5.QtCore import QTimer, Qt, QSize
from PIL import Image, ImageDraw, ImageQt
from io import BytesIO
import speech_recognition as sr
import threading

# Initialize Pygame mixer
pygame.mixer.init()

# Load the music files using glob
music_files = glob.glob("music\\*.mp3")  # Specify your music directory
# Check if music files are found
if not music_files:
    print("No music files found in the specified directory.")
    sys.exit(1)  # Exit if no music files are found

# Current song index
current_song_index = 0

class MusicPlayer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Mossiiccii Player")
        self.init_ui()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_remaining_time)
        self.setStyleSheet("background-color: #ccad60;")

        # Start the voice recognition in a separate thread
        voice_thread = threading.Thread(target=self.start_voice_recognition)
        voice_thread.daemon = True  # This allows the thread to close when the main program exits
        voice_thread.start()

    def init_ui(self):
        # Create a vertical layout for album cover and song name
        layout = QVBoxLayout()
        album_layout = QVBoxLayout()
        album_time_layout = QHBoxLayout()

        # Label to display the album cover
        self.album_cover_label = QLabel(self)
        self.default_cover = QPixmap("icons/cassette.png")  # Default image path
        self.album_cover_label.setPixmap(self.default_cover.scaled(300, 300))  # Increased size
        self.album_cover_label.setStyleSheet("border-radius: 15px;")  # Rounded corners
        album_layout.addWidget(self.album_cover_label, alignment=Qt.AlignLeft)

        # Label to display the currently playing song
        self.label = QLabel("Song Title", self)  # Placeholder text
        self.label.setFont(QFont("Impact", 21, QFont.StyleItalic))  # Set to Italic Impact
        album_layout.addWidget(self.label, alignment=Qt.AlignLeft)  # Add song name under album cover

        # Label to display the remaining time
        self.remaining_time_label = QLabel("00:00", self)
        self.remaining_time_label.setFont(QFont("Impact", 75, QFont.StyleItalic))  # Set to Italic Impact
        self.remaining_time_label.setAlignment(Qt.AlignTop)
        album_layout.addWidget(self.remaining_time_label)

        # Add album layout to the main layout
        layout.addLayout(album_layout)
        
        # Create a horizontal layout for buttons
        button_layout = QHBoxLayout()
        layout.addLayout(album_time_layout)

        # Create buttons with enlarged size
        button_size = (100, 100)  # Adjust size as needed

        # Previous button
        previous_button = QPushButton(self)
        previous_icon = QIcon("icons/previous.png")  # Replace with your previous icon path
        previous_button.setIcon(previous_icon)
        previous_button.setIconSize(QSize(40, 40))  # Set icon size
        previous_button.setFixedSize(*button_size)
        previous_button.setStyleSheet("border: none;")
        previous_button.clicked.connect(self.previous_song)
        button_layout.addWidget(previous_button, alignment=Qt.AlignLeft)

        # Play button
        play_button = QPushButton(self)
        play_icon = QIcon("icons/play.png")  # Replace with your play icon path
        play_button.setIcon(play_icon)
        play_button.setIconSize(QSize(40, 40))  # Set icon size
        play_button.setFixedSize(*button_size)
        play_button.setStyleSheet("border: none;")
        play_button.clicked.connect(self.play)
        button_layout.addWidget(play_button, alignment=Qt.AlignCenter)

        # Pause button
        pause_button = QPushButton(self)
        pause_icon = QIcon("icons/pause.png")  # Replace with your pause icon path
        pause_button.setIcon(pause_icon)
        pause_button.setIconSize(QSize(40, 40))  # Set icon size
        pause_button.setFixedSize(*button_size)
        pause_button.setStyleSheet("border: none;")
        pause_button.clicked.connect(self.pause)
        button_layout.addWidget(pause_button, alignment=Qt.AlignCenter)

        # Next song button
        next_button = QPushButton(self)
        next_icon = QIcon("icons/next.png")  # Replace with your next icon path
        next_button.setIcon(next_icon)
        next_button.setIconSize(QSize(40, 40))  # Set icon size
        next_button.setFixedSize(*button_size)
        next_button.setStyleSheet("border: none;")
        next_button.clicked.connect(self.next_song)
        button_layout.addWidget(next_button, alignment=Qt.AlignRight)

        # Volume Down button
        volume_down_button = QPushButton(self)
        volume_down_icon = QIcon("icons/volume_down.png")  # Replace with your volume down icon path
        volume_down_button.setIcon(volume_down_icon)
        volume_down_button.setIconSize(QSize(40, 40))  # Set icon size
        volume_down_button.setFixedSize(*button_size)
        volume_down_button.setStyleSheet("border: none;")
        volume_down_button.clicked.connect(self.volume_down)
        button_layout.addWidget(volume_down_button, alignment=Qt.AlignRight)

        # Volume Up button
        volume_up_button = QPushButton(self)
        volume_up_icon = QIcon("icons/volume_up.png")  # Replace with your volume up icon path
        volume_up_button.setIcon(volume_up_icon)
        volume_up_button.setIconSize(QSize(40, 40))  # Set icon size
        volume_up_button.setFixedSize(*button_size)
        volume_up_button.setStyleSheet("border: none;")
        volume_up_button.clicked.connect(self.volume_up)
        button_layout.addWidget(volume_up_button, alignment=Qt.AlignRight)

        # Add button layout to the main layout
        layout.addLayout(button_layout)

        # Add stretchable space to push buttons down
        layout.addStretch(1)

        # Container widget to set the layout
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Adjust the window size to fit its contents
        self.adjustSize()

    def listening(self):
        with sr.Microphone() as source:
            print("listening...")
            recognizer = sr.Recognizer()
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source)
        try:
            print("recognizing..... ,\n getting there")
            text = recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Sorry, I could not understand the audio.")
        except sr.RequestError:
            print("Could not request results from the recognition service.")

    def start_voice_recognition(self):
        while True:
            self.acting_commands()
  
    def acting_commands(self):
        command = self.listening()
        if command:
            command = command.lower()
            if "raise the volume" in command:
                self.volume_up()
            elif "lower the volume" in command:
                self.volume_down()
            elif "play next song" in command:
                self.next_song()
                self.play()
            elif "play previous song" in command:
                self.previous_song()
                self.play()
            elif "pause the song" in command:
                self.pause()
            elif "resume the song" in command:
                self.resume()

    def round_corners(self, image, radius):
        # Create a rounded mask
        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0) + image.size, radius=radius, fill=255)
        
        # Apply the mask to the image
        rounded_image = Image.new("RGBA", image.size)
        rounded_image.paste(image, (0, 0), mask)
        return rounded_image

    def update_album_cover(self):
        global current_song_index
        audio_file = music_files[current_song_index]
        try:
            audio = ID3(audio_file)
            for tag in audio.keys():
                if tag.startswith("APIC"):
                    image_data = audio[tag].data
                    image = Image.open(BytesIO(image_data))  # Use BytesIO to open image data
                    
                    # Round the corners of the image
                    rounded_image = self.round_corners(image, radius=15)
                    
                    # Convert the image to a QImage
                    data = rounded_image.tobytes("raw", "RGBA")
                    qt_image = QImage(data, rounded_image.size[0], rounded_image.size[1], QImage.Format_RGBA8888)
                    
                    # Convert QImage to QPixmap
                    pixmap = QPixmap.fromImage(qt_image)
                    
                    # Set the QPixmap to the QLabel
                    self.album_cover_label.setPixmap(pixmap.scaled(300, 300))  # Adjust size as needed
                    break
        except Exception as e:
            print(f"Error loading album cover: {e}")

    def play(self):
        global current_song_index
        pygame.mixer.music.load(music_files[current_song_index])
        pygame.mixer.music.play()
        self.update_album_cover()
        self.update_remaining_time()  # Update the remaining time when the song starts playing

        # Start the timer to update remaining time every second
        self.timer.start(1000)

        # Update the song label
        song_title = os.path.basename(music_files[current_song_index])
        self.label.setText(song_title)

    def pause(self):
        pygame.mixer.music.pause()
        self.timer.stop()  # Stop updating remaining time when paused

    def resume(self):
        pygame.mixer.music.unpause()
        self.timer.start(1000)  # Restart updating remaining time when resumed

    def next_song(self):
        global current_song_index
        current_song_index = (current_song_index + 1) % len(music_files)  # Move to the next song
        self.play()  # Play the next song
        self.update_remaining_time()  # Update remaining time after song changes
        self.timer.start(1000) 

    def previous_song(self):
        global current_song_index
        current_song_index = (current_song_index - 1) % len(music_files)  # Move to the previous song
        self.play()  # Play the previous song
        self.update_remaining_time()  # Update remaining time after song changes

    def update_remaining_time(self):
        audio_file = music_files[current_song_index]
        audio = MP3(audio_file)
        remaining_time = int(audio.info.length - pygame.mixer.music.get_pos() / 1000)  # Calculate remaining time in seconds
        remaining_time_str = f"{remaining_time // 60:02}:{remaining_time % 60:02}"
        self.remaining_time_label.setText(remaining_time_str)

    def volume_up(self):
        current_volume = pygame.mixer.music.get_volume()
        if current_volume < 1.0:  # Maximum volume is 1.0
            pygame.mixer.music.set_volume(current_volume + 0.1)

    def volume_down(self):
        current_volume = pygame.mixer.music.get_volume()
        if current_volume > 0.0:  # Minimum volume is 0.0
            pygame.mixer.music.set_volume(current_volume - 0.1)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = MusicPlayer()
    player.show()
    sys.exit(app.exec_())
