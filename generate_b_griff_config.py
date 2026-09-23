#!/usr/bin/env python3
"""
Generate B-griff configuration file for Bayan MIDI Emulator.
"""

import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bayan_emulator.layout_generators.b_griff import create_b_griff_config

def main():
    """Generate B-griff configuration."""
    config = create_b_griff_config()
    
    # Write to file
    with open("configs/bayan_b_griff_107.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
        
    print("Generated configs/bayan_b_griff_107.json")
    
    # Show statistics
    right_buttons = sum(len(row) for row in config["right_manual"])
    unique_pitches = set()
    for row in config["right_manual"]:
        for button in row:
            unique_pitches.update(button.midi_notes)
    
    print(f"Generated B-griff profile:")
    print(f"  physical buttons = {right_buttons}")
    print(f"  unique pitches = {len(unique_pitches)}")
    print(f"  range = {min(unique_pitches)}..{max(unique_pitches)}")
    print(f"  row1 = {len(config['right_manual'][0])}")
    print(f"  row2 = {len(config['right_manual'][1])}")
    print(f"  row3 = {len(config['right_manual'][2])}")
    print(f"  row4 = {len(config['right_manual'][3])}")
    print(f"  row5 = {len(config['right_manual'][4])}")

if __name__ == "__main__":
    main()
