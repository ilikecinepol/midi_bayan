#!/usr/bin/env python3
"""
Main entry point for Bayan MIDI Emulator GUI application.
"""

import sys
from PySide6.QtWidgets import QApplication
from bayan_emulator.app import BayanApp

def main():
    """Run the Bayan MIDI Emulator application."""
    app = QApplication(sys.argv)
    bayan_app = BayanApp()
    bayan_app.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

