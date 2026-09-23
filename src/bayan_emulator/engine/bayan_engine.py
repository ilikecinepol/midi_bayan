import time
from typing import Set, List, Callable

from ..models.button import BayanButton
from ..models.events import BayanNoteEvent


class BayanEngine:
    def __init__(self):
        self.active_buttons: Set[str] = set()
        self.active_notes: Set[int] = set()
        self.callbacks: List[Callable[[BayanNoteEvent], None]] = []

    def press_button(self, button: BayanButton) -> None:
        # Ignore repeated press of the same physical button.
        if button.id in self.active_buttons:
            return

        self.active_buttons.add(button.id)

        for midi_note in button.midi_notes:
            if midi_note in self.active_notes:
                continue

            self.active_notes.add(midi_note)

            event = BayanNoteEvent(
                source="screen",
                manual=button.manual,
                button_id=button.id,
                event_type="NOTE_ON",
                midi_note=midi_note,
                velocity=100,
                timestamp=time.time(),
            )

            self._emit(event)

    def release_button(self, button: BayanButton) -> None:
        # Ignore release if the button was not pressed.
        if button.id not in self.active_buttons:
            return

        self.active_buttons.remove(button.id)

        for midi_note in button.midi_notes:
            if midi_note not in self.active_notes:
                continue

            self.active_notes.remove(midi_note)

            event = BayanNoteEvent(
                source="screen",
                manual=button.manual,
                button_id=button.id,
                event_type="NOTE_OFF",
                midi_note=midi_note,
                velocity=0,
                timestamp=time.time(),
            )

            self._emit(event)

    def all_notes_off(self) -> None:
        # Send NOTE_OFF for every currently active MIDI note.
        for midi_note in list(self.active_notes):
            event = BayanNoteEvent(
                source="screen",
                manual="unknown",
                button_id="ALL_NOTES_OFF",
                event_type="NOTE_OFF",
                midi_note=midi_note,
                velocity=0,
                timestamp=time.time(),
            )

            self._emit(event)

        self.active_buttons.clear()
        self.active_notes.clear()

    def subscribe(self, callback: Callable[[BayanNoteEvent], None]) -> None:
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def _emit(self, event: BayanNoteEvent) -> None:
        for callback in self.callbacks:
            callback(event)

