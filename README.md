# Bayan MIDI Emulator

Minimal implementation of a bayan MIDI emulator for the first stage.

## Features

- Simulates button presses and releases
- Generates NOTE_ON and NOTE_OFF events
- Supports polyphony and chord buttons
- No GUI or MIDI output in this stage
- Configuration via JSON files

## MIDI Output

To use MIDI output functionality, install dependencies:

```powershell
python -m pip install -e .
python .\tools\midi_smoke_test.py
```

On Windows, the application requires an existing MIDI Output.

This can be:
- a physical MIDI device
- a virtual MIDI port

Do not attempt to create virtual MIDI ports through this application on Windows.

## Configuration

Layouts are stored separately in `configs/` directory to allow multiple instrument configurations without modifying code.
The `bayan_test.json` file is a test configuration, not a complete real layout.