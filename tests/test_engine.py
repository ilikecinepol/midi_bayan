import pytest
from bayan_emulator.models.button import BayanButton
from bayan_emulator.models.events import BayanNoteEvent
from bayan_emulator.engine.bayan_engine import BayanEngine


def test_note_on():
    engine = BayanEngine()
    button = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button)
    
    assert len(events) == 1
    assert events[0].event_type == "NOTE_ON"
    assert events[0].midi_note == 60


def test_note_off():
    engine = BayanEngine()
    button = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button)
    engine.release_button(button)
    
    assert len(events) == 2
    assert events[0].event_type == "NOTE_ON"
    assert events[1].event_type == "NOTE_OFF"
    assert events[0].midi_note == 60
    assert events[1].midi_note == 60


def test_duplicate_press():
    engine = BayanEngine()
    button = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button)
    engine.press_button(button)
    engine.press_button(button)
    
    # Should only generate one NOTE_ON
    assert len(events) == 1
    assert events[0].event_type == "NOTE_ON"
    assert events[0].midi_note == 60


def test_polyphony():
    engine = BayanEngine()
    button1 = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    button2 = BayanButton(
        id="RH_E4",
        manual="right",
        midi_notes=(64,),
        label="E4"
    )
    button3 = BayanButton(
        id="RH_G4",
        manual="right",
        midi_notes=(67,),
        label="G4"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button1)
    engine.press_button(button2)
    engine.press_button(button3)
    
    assert len(events) == 3
    assert engine.active_notes == {60, 64, 67}


def test_release_one_note():
    engine = BayanEngine()
    button1 = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    button2 = BayanButton(
        id="RH_E4",
        manual="right",
        midi_notes=(64,),
        label="E4"
    )
    button3 = BayanButton(
        id="RH_G4",
        manual="right",
        midi_notes=(67,),
        label="G4"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button1)
    engine.press_button(button2)
    engine.press_button(button3)
    engine.release_button(button2)
    
    assert len(events) == 4
    assert engine.active_notes == {60, 67}


def test_chord_button():
    engine = BayanEngine()
    button = BayanButton(
        id="LH_C_MAJOR",
        manual="left",
        midi_notes=(48, 52, 55),
        label="C"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button)
    engine.release_button(button)
    
    assert len(events) == 6  # 3 NOTE_ON + 3 NOTE_OFF
    note_on_events = [e for e in events if e.event_type == "NOTE_ON"]
    note_off_events = [e for e in events if e.event_type == "NOTE_OFF"]
    
    assert len(note_on_events) == 3
    assert len(note_off_events) == 3
    
    # Check that all notes are generated
    note_on_notes = set(e.midi_note for e in note_on_events)
    note_off_notes = set(e.midi_note for e in note_off_events)
    
    assert note_on_notes == {48, 52, 55}
    assert note_off_notes == {48, 52, 55}


def test_all_notes_off():
    engine = BayanEngine()
    button1 = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    button2 = BayanButton(
        id="RH_E4",
        manual="right",
        midi_notes=(64,),
        label="E4"
    )
    
    events = []
    engine.subscribe(events.append)
    engine.press_button(button1)
    engine.press_button(button2)
    engine.all_notes_off()
    
    assert len(events) == 4  # 2 NOTE_ON + 2 NOTE_OFF
    assert engine.active_notes == set()
    assert engine.active_buttons == set()

