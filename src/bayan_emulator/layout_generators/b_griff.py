"""
B-griff layout generator for the right manual of a bayan.
"""

from bayan_emulator.models.button import BayanButton


NOTE_NAMES = (
    "C",
    "C#",
    "D",
    "D#",
    "E",
    "F",
    "F#",
    "G",
    "G#",
    "A",
    "A#",
    "B",
)


def midi_to_note_name(note: int) -> str:
    """Convert MIDI note number to note name, e.g. 60 -> C4."""

    if not 0 <= note <= 127:
        raise ValueError(
            f"MIDI note must be between 0 and 127, got {note}"
        )

    note_name = NOTE_NAMES[note % 12]
    octave = (note // 12) - 1

    return f"{note_name}{octave}"


def generate_b_griff_right_manual(
    midi_min: int = 40,
    midi_max: int = 103,
) -> tuple[BayanButton, ...]:
    """
    Generate five-row B-griff right manual.

    Reference layout:

    Row 1:
        G, A#, C#, E ...

    Row 2:
        G#, B, D, F ...

    Row 3:
        F#, A, C, D# ...

    Row 4 duplicates Row 1.
    Row 5 duplicates Row 2.
    """

    if not 0 <= midi_min <= 127:
        raise ValueError("midi_min must be within 0..127")

    if not 0 <= midi_max <= 127:
        raise ValueError("midi_max must be within 0..127")

    if midi_min > midi_max:
        raise ValueError("midi_min must be <= midi_max")

    row1: list[int] = []
    row2: list[int] = []
    row3: list[int] = []

    for midi_note in range(midi_min, midi_max + 1):
        remainder = midi_note % 3

        # Row 1:
        # C#, E, G, A#
        if remainder == 1:
            row1.append(midi_note)

        # Row 2:
        # D, F, G#, B
        elif remainder == 2:
            row2.append(midi_note)

        # Row 3:
        # C, D#, F#, A
        else:
            row3.append(midi_note)

    # Additional two physical rows
    # duplicate the first two rows.
    row4 = list(row1)
    row5 = list(row2)

    row_map = {
        1: row1,
        2: row2,
        3: row3,
        4: row4,
        5: row5,
    }

    buttons: list[BayanButton] = []

    for physical_row, midi_notes in row_map.items():
        for index, midi_note in enumerate(midi_notes):
            buttons.append(
                BayanButton(
                    id=f"RH_R{physical_row}_M{midi_note}",
                    manual="right",
                    midi_notes=(midi_note,),
                    label=midi_to_note_name(midi_note),
                    row=physical_row,
                    index=index,
                    computer_key=None,
                    button_type="note",
                )
            )

    return tuple(buttons)


def create_test_left_manual() -> tuple[BayanButton, ...]:
    """
    Temporary left manual.
    Full bass/chord keyboard will be implemented separately.
    """

    return (
        BayanButton(
            id="LH_C_BASS",
            manual="left",
            midi_notes=(36,),
            label="C",
            row=2,
            index=0,
            computer_key=None,
            button_type="bass",
        ),
        BayanButton(
            id="LH_C_MAJOR",
            manual="left",
            midi_notes=(48, 52, 55),
            label="C",
            row=3,
            index=0,
            computer_key=None,
            button_type="major_chord",
        ),
    )


def create_b_griff_config() -> dict:
    """Create complete B-griff configuration."""

    return {
        "instrument": "bayan",
        "layout_name": "B-Griff 107 E2-G7",
        "right_manual": generate_b_griff_right_manual(),
        "left_manual": create_test_left_manual(),
    }