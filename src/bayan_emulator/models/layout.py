from dataclasses import dataclass
from typing import Tuple
from .button import BayanButton


@dataclass
class BayanLayout:
    instrument: str
    layout_name: str
    right_manual: Tuple[BayanButton, ...]
    left_manual: Tuple[BayanButton, ...]

