"""
MIDI monitor for displaying MIDI events.
"""

from PySide6.QtWidgets import QPlainTextEdit
from PySide6.QtCore import Qt

from bayan_emulator.models.events import BayanNoteEvent


class MidiMonitor(QPlainTextEdit):
    """Display MIDI events in a text area."""
    
    def __init__(self):
        """Initialize the MIDI monitor."""
        super().__init__()
        
        self.setReadOnly(True)
        self.setMaximumHeight(100)
    
    def handle_event(self, event: BayanNoteEvent):
        """Handle bayan note events and display them."""
        # Format the event for display
        if event.event_type == "NOTE_ON":
            text = f"NOTE_ON  {event.manual} {event.button_id:<12} note={event.midi_note:3d} velocity={event.velocity:3d}"
        elif event.event_type == "NOTE_OFF":
            text = f"NOTE_OFF {event.manual} {event.button_id:<12} note={event.midi_note:3d}"
        else:
            return  # Skip unknown events
            
        # Add to monitor
        self.appendPlainText(text)
        
        # Scroll to bottom
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

