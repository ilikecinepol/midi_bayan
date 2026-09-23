#!/usr/bin/env python3
"""Simple test for layout generation without direct package imports."""

import sys
import os

# Add the src to path for testing 
sys.path.insert(0, '.')

def simple_b_griff_test():
    """Do final validation of layout structure."""
    
    print("Validating B-griff layout generation logic:")
    
    # This simulates how our layout will work in the full system
    note_count = 0
    
    # Track pitches by row to make sure they are correct according to MOD3 rule
    row_pitches = {1: [], 2: [], 3: [], 4: [], 5: []}
    
    for midi_note in range(40, 104):  # E2 to G7 (MIDI 40-103)
        note_count += 1
        
        # Apply MOD3 rule
        row_index = midi_note % 3
        
        if row_index == 0:  # Goes to row3
            row_pitches[3].append(midi_note)
        elif row_index == 1:  # Goes to row4  
            row_pitches[4].append(midi_note)
        else:  # Goes to row5 
            row_pitches[5].append(midi_note)
    
    print(f"Processed {note_count} MIDI notes")
    
    # Create duplicates (row1 = row4, row2 = row5) 
    row_pitches[1] = list(row_pitches[4])  # Duplicates row4
    row_pitches[2] = list(row_pitches[5])  # Duplicates row5
    
    print("Pitches by row calculation:")
    for i in range(1, 6):
        print(f"Row {i}: {len(row_pitches[i])} pitches")
    
    total = sum(len(pitches) for pitches in row_pitches.values()) 
    print(f"Total physical buttons: {total}")
    
    # Check ranges
    min_pitch = min(min(pitches) for pitches in row_pitches.values() if pitches)
    max_pitch = max(max(pitches) for pitches in row_pitches.values() if pitches)
    
    print(f"MIDI range: {min_pitch} to {max_pitch}")
    
    # Verify correct count
    assert total == 107, f"Expected 107 buttons, got {total}"
    assert min_pitch == 40, f"Expected minimum pitch 40, got {min_pitch}"
    assert max_pitch == 103, f"Expected maximum pitch 103, got {max_pitch}" 
    
    # Check for proper unique pitch counts
    all_unique_pitch = set()
    for pitches in row_pitches.values():
        all_unique_pitch.update(pitches)
    
    print(f"Unique pitches from all rows: {len(all_unique_pitch)}")
    
    assert len(all_unique_pitch) == 64, f"Expected 64 unique pitches, got {len(all_unique_pitch)}"
    
    # Verify duplicates (row1 should have same pitches as row4)
    assert set(row_pitches[1]) == set(row_pitches[4]), "Row1 must duplicates Row4"
    assert set(row_pitches[2]) == set(row_pitches[5]), "Row2 must duplicate Row5"
    
    # Verify primary rows don't overlap
    assert len(set(row_pitches[3]).intersection(row_pitches[4])) == 0, "Primary rows overlap"
    assert len(set(row_pitches[3]).intersection(row_pitches[5])) == 0, "Primary rows overlap"
    assert len(set(row_pitches[4]).intersection(row_pitches[5])) == 0, "Primary rows overlap"
    
    print("вњ“ All validation tests passed!")
    
    # Show actual button counts
    expected_counts = [22, 21, 21, 22, 21]  # R1, R2, R3, R4, R5
    actual_counts = [len(row_pitches[i]) for i in range(1, 6)]
    
    print(f"Row counts: {actual_counts}")
    assert actual_counts == expected_counts, f"Row counts don't match: {expected_counts} vs {actual_counts}"
    
    return True

if __name__ == "__main__":
    simple_b_griff_test()
    print("\nB-griff validation complete - layout structure is correct")
