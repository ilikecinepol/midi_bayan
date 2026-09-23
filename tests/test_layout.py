import pytest
from bayan_emulator.models.layout import BayanLayout
from bayan_emulator.models.button import BayanButton


def test_bayan_layout_creation():
    # Create some test buttons
    right_button = BayanButton(
        id="RH_C4",
        manual="right",
        midi_notes=(60,),
        label="C4"
    )
    
    left_button = BayanButton(
        id="LH_C_BASS",
        manual="left",
        midi_notes=(36,),
        label="C"
    )
    
    # Create layout
    layout = BayanLayout(
        instrument="bayan",
        layout_name="Test Layout",
        right_manual=(right_button,),
        left_manual=(left_button,)
    )
    
    assert layout.instrument == "bayan"
    assert layout.layout_name == "Test Layout"
    assert len(layout.right_manual) == 1
    assert len(layout.left_manual) == 1

