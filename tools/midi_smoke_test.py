import time

from bayan_emulator.config.loader import load_layout
from bayan_emulator.engine.bayan_engine import BayanEngine
from bayan_emulator.midi.output import MidiOutputService


def main() -> None:
    print("MIDI Output Smoke Test")
    print("=" * 25)

    midi = MidiOutputService()
    ports = midi.list_ports()

    if not ports:
        print("No MIDI output ports found.")
        print("On Windows, connect a physical or virtual MIDI device.")
        return

    print("\nAvailable MIDI outputs:")

    for index, port in enumerate(ports):
        print(f"[{index}] {port}")

    if len(ports) == 1:
        selected_port = ports[0]
        print(f"\nUsing: {selected_port}")
    else:
        try:
            choice = input("\nSelect MIDI output index: ")
            index = int(choice)

            if index < 0 or index >= len(ports):
                print("Invalid port index.")
                return

            selected_port = ports[index]

        except (ValueError, KeyboardInterrupt):
            print("\nCancelled.")
            return

    try:
        print(f"\nOpening MIDI output: {selected_port}")
        midi.open_port(selected_port)

        # Load the test bayan layout
        layout = load_layout("configs/bayan_test.json")

        # Find C4 button
        button = next(
            button
            for button in layout.right_manual
            if button.id == "RH_C4"
        )

        # Create real bayan engine
        engine = BayanEngine()

        # Connect engine events to real MIDI output
        engine.subscribe(midi.handle_event)

        print("\nPressing virtual bayan button RH_C4")
        print("Sending NOTE_ON: C4 / MIDI 60")

        engine.press_button(button)

        time.sleep(1)

        print("Sending NOTE_OFF: C4 / MIDI 60")

        engine.release_button(button)

        print("\nDone.")

    except Exception as exc:
        print(f"\nError during MIDI test: {exc}")

    finally:
        midi.close()


if __name__ == "__main__":
    main()
