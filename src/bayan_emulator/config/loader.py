import json
from typing import Any, Dict

from ..models.button import BayanButton
from ..models.layout import BayanLayout


class LayoutConfigError(Exception):
    pass


def load_layout(path: str) -> BayanLayout:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate instrument
    if "instrument" not in data:
        raise LayoutConfigError("Missing instrument field")

    if data["instrument"] != "bayan":
        raise LayoutConfigError(
            f"Invalid instrument: {data['instrument']}"
        )

    # Validate manual fields
    if "right_manual" not in data:
        raise LayoutConfigError("Missing right_manual field")

    if "left_manual" not in data:
        raise LayoutConfigError("Missing left_manual field")

    # Collect all button IDs to check for duplicates
    all_ids = set()

    # Load right manual buttons
    right_buttons = []

    for btn_data in data["right_manual"]:
        _validate_button_data(btn_data, "right")

        if btn_data["id"] in all_ids:
            raise LayoutConfigError(
                f"Duplicate button id: {btn_data['id']}"
            )

        all_ids.add(btn_data["id"])

        button = BayanButton(
            **{
                **btn_data,
                "midi_notes": tuple(btn_data["midi_notes"]),
            }
        )

        right_buttons.append(button)

    # Load left manual buttons
    left_buttons = []

    for btn_data in data["left_manual"]:
        _validate_button_data(btn_data, "left")

        if btn_data["id"] in all_ids:
            raise LayoutConfigError(
                f"Duplicate button id: {btn_data['id']}"
            )

        all_ids.add(btn_data["id"])

        button = BayanButton(
            **{
                **btn_data,
                "midi_notes": tuple(btn_data["midi_notes"]),
            }
        )

        left_buttons.append(button)

    return BayanLayout(
        instrument=data["instrument"],
        layout_name=data.get("layout_name", ""),
        right_manual=tuple(right_buttons),
        left_manual=tuple(left_buttons),
    )


def _validate_button_data(
    btn_data: Dict[str, Any],
    expected_manual: str,
) -> None:

    # Validate id
    if "id" not in btn_data or not btn_data["id"]:
        raise LayoutConfigError("Button ID is required")

    # Validate manual
    if "manual" not in btn_data:
        raise LayoutConfigError(
            f"Missing manual field for button {btn_data['id']}"
        )

    if btn_data["manual"] != expected_manual:
        raise LayoutConfigError(
            f"Button {btn_data['id']} has incorrect manual. "
            f"Expected '{expected_manual}', "
            f"got '{btn_data['manual']}'"
        )

    # Validate midi_notes
    if "midi_notes" not in btn_data:
        raise LayoutConfigError(
            f"Missing midi_notes for button {btn_data['id']}"
        )

    if not isinstance(btn_data["midi_notes"], list):
        raise LayoutConfigError(
            f"midi_notes must be a list for button {btn_data['id']}"
        )

    if len(btn_data["midi_notes"]) == 0:
        raise LayoutConfigError(
            f"Empty midi_notes for button {btn_data['id']}"
        )

    for note in btn_data["midi_notes"]:
        if not isinstance(note, int) or note < 0 or note > 127:
            raise LayoutConfigError(
                f"Invalid MIDI note {note} "
                f"for button {btn_data['id']}. "
                f"MIDI notes must be integers between 0 and 127"
            )

