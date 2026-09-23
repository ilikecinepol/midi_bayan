"""
Main application class for Bayan MIDI Emulator.
"""

import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from bayan_emulator.ui.main_window import MainWindow


class BayanApp(QMainWindow):
    """Main application class."""
    
    def __init__(self):
        """Initialize the main application."""
        super().__init__()
        self.main_window = MainWindow()
        self.setCentralWidget(self.main_window)
        self.setWindowTitle("Bayan MIDI Emulator")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

