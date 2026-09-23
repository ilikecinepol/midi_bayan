import pytest
import os
from bayan_emulator.config.loader import load_layout, LayoutConfigError
from bayan_emulator.models.button import BayanButton
from bayan_emulator.models.layout import BayanLayout


def test_load_layout():
    layout = load_layout('configs/bayan_test.json')
    
    assert layout.instrument == "bayan"
    assert len(layout.right_manual) == 2
    assert len(layout.left_manual) == 2


def test_right_button():
    layout = load_layout('configs/bayan_test.json')
    
    button = None
    for btn in layout.right_manual:
        if btn.id == "RH_C4":
            button = btn
            break
    
    assert button is not None
    assert button.midi_notes == (60,)


def test_chord_button():
    layout = load_layout('configs/bayan_test.json')
    
    button = None
    for btn in layout.left_manual:
        if btn.id == "LH_C_MAJOR":
            button = btn
            break
    
    assert button is not None
    assert button.midi_notes == (48, 52, 55)


def test_duplicate_id():
    # Create a temporary JSON with duplicate IDs
    duplicate_json = '''
    {
      "instrument": "bayan",
      "right_manual": [
        {
          "id": "RH_C4",
          "manual": "right",
          "midi_notes": [60]
        },
        {
          "id": "RH_C4",
          "manual": "right",
          "midi_notes": [64]
        }
      ],
      "left_manual": []
    }
    '''
    
    with open('configs/duplicate_test.json', 'w') as f:
        f.write(duplicate_json)
    
    with pytest.raises(LayoutConfigError) as excinfo:
        load_layout('configs/duplicate_test.json')
    
    assert "Duplicate button id" in str(excinfo.value)
    
    # Clean up
    os.remove('configs/duplicate_test.json')


def test_invalid_midi():
    # Create a temporary JSON with invalid MIDI note
    invalid_midi_json = '''
    {
      "instrument": "bayan",
      "right_manual": [
        {
          "id": "RH_X",
          "manual": "right",
          "midi_notes": [140]
        }
      ],
      "left_manual": []
    }
    '''
    
    with open('configs/invalid_midi_test.json', 'w') as f:
        f.write(invalid_midi_json)
    
    with pytest.raises(LayoutConfigError) as excinfo:
        load_layout('configs/invalid_midi_test.json')
    
    assert "Invalid MIDI note" in str(excinfo.value)
    
    # Clean up
    os.remove('configs/invalid_midi_test.json')


def test_empty_midi_notes():
    # Create a temporary JSON with empty midi_notes
    empty_midi_json = '''
    {
      "instrument": "bayan",
      "right_manual": [
        {
          "id": "RH_X",
          "manual": "right",
          "midi_notes": []
        }
      ],
      "left_manual": []
    }
    '''
    
    with open('configs/empty_midi_test.json', 'w') as f:
        f.write(empty_midi_json)
    
    with pytest.raises(LayoutConfigError) as excinfo:
        load_layout('configs/empty_midi_test.json')
    
    assert "Empty midi_notes" in str(excinfo.value)
    
    # Clean up
    os.remove('configs/empty_midi_test.json')


def test_wrong_manual():
    # Create a temporary JSON with wrong manual
    wrong_manual_json = '''
    {
      "instrument": "bayan",
      "right_manual": [
        {
          "id": "RH_X",
          "manual": "left",
          "midi_notes": [60]
        }
      ],
      "left_manual": []
    }
    '''
    
    with open('configs/wrong_manual_test.json', 'w') as f:
        f.write(wrong_manual_json)
    
    with pytest.raises(LayoutConfigError) as excinfo:
        load_layout('configs/wrong_manual_test.json')
    
    assert "incorrect manual" in str(excinfo.value)
    
    # Clean up
    os.remove('configs/wrong_manual_test.json')


def test_integration():
    layout = load_layout('configs/bayan_test.json')
    
    # Find the C4 button 
    c4_button = None
    for btn in layout.right_manual:
        if btn.id == "RH_C4":
            c4_button = btn
            break
    
    assert c4_button is not None
    
    # Import the engine and test integration
    from bayan_emulator.engine.bayan_engine import BayanEngine
    from bayan_emulator.models.events import BayanNoteEvent
    
    # Set up engine 
    engine = BayanEngine()
    events = []
    engine.subscribe(events.append)
    
    # Press the button and check event generation 
    engine.press_button(c4_button)
    
    assert len(events) == 1
    assert events[0].event_type == "NOTE_ON"
    assert events[0].midi_note == 60

