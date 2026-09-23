import json
from dataclasses import asdict, is_dataclass
from pathlib import Path

from bayan_emulator.layout_generators.b_griff import create_b_griff_config


def button_to_dict(button):
    if is_dataclass(button):
        data = asdict(button)
    elif isinstance(button, dict):
        data = dict(button)
    else:
        raise TypeError(
            f"Unsupported button type: {type(button).__name__}"
        )

    if "midi_notes" in data:
        data["midi_notes"] = list(data["midi_notes"])

    return data


def flatten_buttons(items):
    """Flatten nested rows/lists into a single button list."""
    result = []

    for item in items:
        if isinstance(item, (list, tuple)):
            result.extend(flatten_buttons(item))
        else:
            result.append(item)

    return result


def main():
    project_root = Path(__file__).resolve().parents[1]

    output_path = (
        project_root
        / "configs"
        / "bayan_b_griff_107.json"
    )

    config = create_b_griff_config()

    raw_right = config["right_manual"]
    raw_left = config["left_manual"]

    print("Config type:", type(config).__name__)
    print(
        "Right top-level item type:",
        type(raw_right[0]).__name__
        if raw_right else "EMPTY"
    )

    flat_right = flatten_buttons(raw_right)
    flat_left = flatten_buttons(raw_left)

    right_manual = [
        button_to_dict(button)
        for button in flat_right
    ]

    left_manual = [
        button_to_dict(button)
        for button in flat_left
    ]

    json_config = {
        "instrument": config["instrument"],
        "layout_name": config["layout_name"],
        "right_manual": right_manual,
        "left_manual": left_manual,
    }

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            json_config,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print(f"Generated: {output_path}")
    print(f"Right buttons: {len(right_manual)}")
    print(f"Left buttons: {len(left_manual)}")


if __name__ == "__main__":
    main()