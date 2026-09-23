import mido
from typing import List, Optional
from ..models.events import BayanNoteEvent


class MidiOutputError(Exception):
    pass


class MidiOutputService:
    def __init__(self) -> None:
        self._port = None
        self._is_open = False
        self._current_port_name: Optional[str] = None
    
    @property
    def is_open(self) -> bool:
        return self._is_open
    
    @property
    def current_port_name(self) -> Optional[str]:
        return self._current_port_name
    
    def list_ports(self) -> List[str]:
        """Return list of available MIDI output ports."""
        try:
            return mido.get_output_names()
        except Exception:
            # Return empty list if there's an error
            return []
    
    def open_port(self, name: str) -> None:
        """Open a MIDI output port."""
        # Close any existing port
        self.close()
        
        try:
            self._port = mido.open_output(name)
            self._is_open = True
            self._current_port_name = name
        except Exception as exc:
            raise MidiOutputError(f"Failed to open MIDI port '{name}': {str(exc)}") from exc
    
    def close(self) -> None:
        """Stop all notes and close the current MIDI output."""
        if self._port is not None:
            try:
                self.panic()
            except Exception:
                pass

            try:
                self._port.close()
            except Exception:
                pass

        self._port = None
        self._is_open = False
        self._current_port_name = None
    
    def handle_event(self, event: BayanNoteEvent) -> None:
        """Handle a BayanNoteEvent and send MIDI message."""
        if not self._is_open or self._port is None:
            # If no port is open, just ignore the event
            return
        
        try:
            if event.event_type == "NOTE_ON":
                msg = mido.Message(
                    "note_on",
                    note=event.midi_note,
                    velocity=event.velocity,
                    channel=0
                )
                self._port.send(msg)
                
            elif event.event_type == "NOTE_OFF":
                msg = mido.Message(
                    "note_off",
                    note=event.midi_note,
                    velocity=0,
                    channel=0
                )
                self._port.send(msg)
        except Exception as exc:
            # Silently ignore MIDI sending errors to not break the application
            pass
    
    def panic(self) -> None:
        if self._port is None:
            return

        for channel in range(16):
            # All Sound Off
            self._port.send(
                mido.Message(
                    "control_change",
                    channel=channel,
                    control=120,
                    value=0,
                )
            )

            # All Notes Off
            self._port.send(
                mido.Message(
                    "control_change",
                    channel=channel,
                    control=123,
                    value=0,
                )
            )

