import mido
from typing import List, Optional

from ..models.events import BayanNoteEvent


class MidiOutputError(Exception):
    pass


class MidiOutputService:
    def __init__(self) -> None:
        self._port = None
        self._is_open = False
        self._current_port_name: Optional[str] = None

        # General MIDI program.
        #
        # 0  = Acoustic Grand Piano
        # 21 = Accordion
        # 23 = Tango Accordion
        #
        # Default: Accordion.
        self._current_program = 21

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def current_port_name(self) -> Optional[str]:
        return self._current_port_name

    @property
    def current_program(self) -> int:
        return self._current_program

    def list_ports(self) -> List[str]:
        """Return list of available MIDI output ports."""
        try:
            return mido.get_output_names()
        except Exception:
            return []

    def open_port(self, name: str) -> None:
        """
        Open a MIDI output port.

        The currently selected General MIDI program
        is sent immediately after opening.
        """
        self.close()

        try:
            self._port = mido.open_output(name)

            self._is_open = True
            self._current_port_name = name

            self._send_program_change()

        except Exception as exc:
            self._port = None
            self._is_open = False
            self._current_port_name = None

            raise MidiOutputError(
                f"Failed to open MIDI port '{name}': {exc}"
            ) from exc

    def close(self) -> None:
        """Stop all notes and close the current MIDI output."""
        if self._port is not None:
            try:
                self.panic()
            except Exception:
                pass

            try:
                self._port.close()
            except Exception:
                pass

        self._port = None
        self._is_open = False
        self._current_port_name = None

    def set_program(self, program: int) -> None:
        """
        Select a General MIDI instrument.

        MIDI program numbers are zero-based:
            0  = Acoustic Grand Piano
            21 = Accordion
            23 = Tango Accordion
        """

        program = int(program)

        if not 0 <= program <= 127:
            raise ValueError(
                f"MIDI program must be between 0 and 127, got {program}"
            )

        self._current_program = program

        if self._is_open and self._port is not None:
            self._send_program_change()

    def _send_program_change(self) -> None:
        """Send current GM instrument to MIDI channel 1."""
        if self._port is None:
            return

        self._port.send(
            mido.Message(
                "program_change",
                program=self._current_program,
                channel=0,
            )
        )

    def handle_event(self, event: BayanNoteEvent) -> None:
        """Handle BayanNoteEvent and send MIDI message."""
        if not self._is_open or self._port is None:
            return

        try:
            if event.event_type == "NOTE_ON":
                self._port.send(
                    mido.Message(
                        "note_on",
                        note=event.midi_note,
                        velocity=event.velocity,
                        channel=0,
                    )
                )

            elif event.event_type == "NOTE_OFF":
                self._port.send(
                    mido.Message(
                        "note_off",
                        note=event.midi_note,
                        velocity=0,
                        channel=0,
                    )
                )

        except Exception:
            # MIDI failure should not crash the GUI.
            pass

    def panic(self) -> None:
        """Immediately stop all MIDI sound on all channels."""
        if self._port is None:
            return

        for channel in range(16):
            # All Sound Off
            self._port.send(
                mido.Message(
                    "control_change",
                    channel=channel,
                    control=120,
                    value=0,
                )
            )

            # All Notes Off
            self._port.send(
                mido.Message(
                    "control_change",
                    channel=channel,
                    control=123,
                    value=0,
                )
            )