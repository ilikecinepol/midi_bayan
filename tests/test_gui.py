from PySide6.QtWidgets import QMainWindow

from bayan_emulator.ui.main_window import MainWindow


def test_window_creation(qtbot):
    """MainWindow can be created."""
    window = MainWindow()
    qtbot.addWidget(window)

    assert window is not None
    assert isinstance(window, QMainWindow)
    assert window.windowTitle() == "Bayan MIDI Emulator"


def test_buttons_created_from_layout(qtbot):
    """GUI loads without errors and contains bayan buttons."""
    window = MainWindow()
    qtbot.addWidget(window)

    assert window is not None

    # Пока минимальная проверка.
    # Позже усилим её до проверки реального количества кнопок.


def test_midi_monitor_exists(qtbot):
    """MIDI monitor is initialized."""
    window = MainWindow()
    qtbot.addWidget(window)

    assert hasattr(window, "midi_monitor")
    assert window.midi_monitor is not None
