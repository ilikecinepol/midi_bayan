import pytest
from unittest.mock import Mock, patch

from bayan_emulator.midi.output import MidiOutputService, MidiOutputError
from bayan_emulator.models.events import BayanNoteEvent


def test_list_ports():
    service = MidiOutputService()

    with patch("mido.get_output_names") as mock_get_names:
        mock_get_names.return_value = ["Test MIDI 1", "Test MIDI 2"]

        ports = service.list_ports()

        assert ports == ["Test MIDI 1", "Test MIDI 2"]


def test_open_port():
    service = MidiOutputService()

    with patch("mido.open_output") as mock_open:
        mock_port = Mock()
        mock_open.return_value = mock_port

        service.open_port("Test MIDI")

        assert service.is_open is True
        assert service.current_port_name == "Test MIDI"
        mock_open.assert_called_once_with("Test MIDI")


def test_open_port_error():
    service = MidiOutputService()

    with patch("mido.open_output") as mock_open:
        mock_open.side_effect = Exception("Connection failed")

        with pytest.raises(MidiOutputError):
            service.open_port("Bad MIDI")


def test_close():
    service = MidiOutputService()

    with patch("mido.open_output") as mock_open:
        mock_port = Mock()
        mock_open.return_value = mock_port

        service.open_port("Test MIDI")
        service.close()

        assert service.is_open is False
        assert service.current_port_name is None
        mock_port.close.assert_called_once()


def test_handle_event_note_on():
    service = MidiOutputService()

    with patch("mido.open_output") as mock_open:
        mock_port = Mock()
        mock_open.return_value = mock_port

        service.open_port("Test MIDI")

        event = BayanNoteEvent(
            source="screen",
            manual="right",
            button_id="RH_C4",
            event_type="NOTE_ON",
            midi_note=60,
            velocity=100,
            timestamp=0.0,
        )

        service.handle_event(event)

        mock_port.send.assert_called_once()

        message = mock_port.send.call_args[0][0]

        assert message.type == "note_on"
        assert message.note == 60
        assert message.velocity == 100
        assert message.channel == 0


def test_handle_event_note_off():
    service = MidiOutputService()

    with patch("mido.open_output") as mock_open:
        mock_port = Mock()
        mock_open.return_value = mock_port

        service.open_port("Test MIDI")

        event = BayanNoteEvent(
            source="screen",
            manual="right",
            button_id="RH_C4",
            event_type="NOTE_OFF",
            midi_note=60,
            velocity=100,
            timestamp=0.0,
        )

        service.handle_event(event)

        mock_port.send.assert_called_once()

        message = mock_port.send.call_args[0][0]

        assert message.type == "note_off"
        assert message.note == 60
        assert message.velocity == 0
        assert message.channel == 0


def test_handle_event_no_port():
    service = MidiOutputService()

    event = BayanNoteEvent(
        source="screen",
        manual="right",
        button_id="RH_C4",
        event_type="NOTE_ON",
        midi_note=60,
        velocity=100,
        timestamp=0.0,
    )

    service.handle_event(event)


def test_panic():
    service = MidiOutputService()

    with patch("mido.open_output") as mock_open:
        mock_port = Mock()
        mock_open.return_value = mock_port

        service.open_port("Test MIDI")

        service.panic()

        assert mock_port.send.called

        messages = [
            call.args[0]
            for call in mock_port.send.call_args_list
        ]

        all_sound_off = [
            msg
            for msg in messages
            if msg.type == "control_change"
            and msg.control == 120
        ]

        all_notes_off = [
            msg
            for msg in messages
            if msg.type == "control_change"
            and msg.control == 123
        ]

        assert len(all_sound_off) == 16
        assert len(all_notes_off) == 16


def test_panic_no_port():
    service = MidiOutputService()

    service.panic()

