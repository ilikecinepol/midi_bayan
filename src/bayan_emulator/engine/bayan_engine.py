import time
from typing import Set, List, Callable

from ..models.button import BayanButton
from ..models.events import BayanNoteEvent


class BayanEngine:
    def __init__(self):
        self.active_buttons: Set[str] = set()
        self.active_notes: Set[int] = set()

        # One MIDI pitch may exist on several physical
        # buttons of the five-row bayan keyboard.
        self._note_ref_counts: dict[int, int] = {}

        self.callbacks: List[
            Callable[[BayanNoteEvent], None]
        ] = []

    def press_button(
        self,
        button: BayanButton,
        source: str = "screen",
    ) -> None:
        if button.id in self.active_buttons:
            return

        self.active_buttons.add(button.id)

        for midi_note in button.midi_notes:
            count = self._note_ref_counts.get(
                midi_note,
                0,
            )

            self._note_ref_counts[midi_note] = (
                count + 1
            )

            # Another physical button is already
            # holding the same MIDI pitch.
            if count > 0:
                continue

            self.active_notes.add(midi_note)

            event = BayanNoteEvent(
                source=source,
                manual=button.manual,
                button_id=button.id,
                event_type="NOTE_ON",
                midi_note=midi_note,
                velocity=100,
                timestamp=time.time(),
            )

            self._emit(event)

    def release_button(
        self,
        button: BayanButton,
        source: str = "screen",
    ) -> None:
        if button.id not in self.active_buttons:
            return

        self.active_buttons.remove(button.id)

        for midi_note in button.midi_notes:
            count = self._note_ref_counts.get(
                midi_note,
                0,
            )

            if count <= 0:
                continue

            if count > 1:
                self._note_ref_counts[
                    midi_note
                ] = count - 1

                continue

            self._note_ref_counts.pop(
                midi_note,
                None,
            )

            self.active_notes.discard(
                midi_note
            )

            event = BayanNoteEvent(
                source=source,
                manual=button.manual,
                button_id=button.id,
                event_type="NOTE_OFF",
                midi_note=midi_note,
                velocity=0,
                timestamp=time.time(),
            )

            self._emit(event)

    def all_notes_off(self) -> None:
        for midi_note in list(
            self.active_notes
        ):
            event = BayanNoteEvent(
                source="system",
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
        self._note_ref_counts.clear()

    def subscribe(
        self,
        callback: Callable[
            [BayanNoteEvent],
            None,
        ],
    ) -> None:
        if callback not in self.callbacks:
            self.callbacks.append(callback)

    def _emit(
        self,
        event: BayanNoteEvent,
    ) -> None:
        for callback in self.callbacks:
            callback(event)