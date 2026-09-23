from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class BayanButton:
    id: str
    manual: str  # right or left
    midi_notes: Tuple[int, ...]
    label: str = ""
    row: Optional[int] = None
    index: Optional[int] = None
    computer_key: Optional[str] = None
    button_type: str = "note"

