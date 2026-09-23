from dataclasses import dataclass


@dataclass
class BayanNoteEvent:
    source: str
    manual: str
    button_id: str
    event_type: str  # NOTE_ON or NOTE_OFF
    midi_note: int
    velocity: int
    timestamp: float


