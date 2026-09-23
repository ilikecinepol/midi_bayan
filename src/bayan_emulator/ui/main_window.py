"""
Main window for Bayan MIDI Emulator GUI.
"""

from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtWidgets import (
    QComboBox,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from bayan_emulator.config.loader import load_layout
from bayan_emulator.engine.bayan_engine import BayanEngine
from bayan_emulator.midi.output import MidiOutputService
from bayan_emulator.ui.bayan_button import BayanButtonWidget
from bayan_emulator.ui.midi_monitor import MidiMonitor


class MainWindow(QMainWindow):
    """Main window with bayan interface and MIDI controls."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bayan MIDI Emulator")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        self.engine = BayanEngine()
        self.midi_output = MidiOutputService()

        self.button_widgets: dict[str, BayanButtonWidget] = {}

        project_root = Path(__file__).resolve().parents[3]

        config_path = (
            project_root
            / "configs"
            / "bayan_b_griff_107.json"
        )

        self.layout = load_layout(str(config_path))

        self.engine.subscribe(
            self.midi_output.handle_event
        )

        self.init_ui()
        self.setup_connections()

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)

        main_layout.addWidget(
            self.create_top_panel()
        )

        main_layout.addWidget(
            self.create_middle_panel(),
            1,
        )

        main_layout.addWidget(
            self.create_bottom_panel()
        )

    def create_top_panel(self):
        panel = QWidget()
        layout = QHBoxLayout(panel)

        layout.setSpacing(10)

        layout.addWidget(
            QLabel("MIDI Output:")
        )

        self.midi_combo = QComboBox()

        layout.addWidget(
            self.midi_combo,
            1,
        )

        self.refresh_btn = QPushButton(
            "Refresh"
        )

        self.refresh_btn.clicked.connect(
            self.update_midi_ports
        )

        layout.addWidget(
            self.refresh_btn
        )

        self.connect_btn = QPushButton(
            "Connect"
        )

        self.connect_btn.clicked.connect(
            self.connect_midi
        )

        layout.addWidget(
            self.connect_btn
        )

        self.status_label = QLabel(
            "Status: Not connected"
        )

        self.status_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            self.status_label
        )

        self.update_midi_ports()

        return panel

    def create_middle_panel(self):
        panel = QWidget()
        layout = QHBoxLayout(panel)

        layout.setSpacing(30)

        left_manual = self.create_manual_panel(
            "LEFT MANUAL",
            self.layout.left_manual,
        )

        layout.addWidget(
            left_manual,
            1,
        )

        bellows = QFrame()

        bellows.setFrameShape(
            QFrame.VLine
        )

        bellows.setFrameShadow(
            QFrame.Sunken
        )

        bellows.setMinimumWidth(80)

        layout.addWidget(
            bellows
        )

        right_manual = self.create_manual_panel(
            "RIGHT MANUAL",
            self.layout.right_manual,
        )

        layout.addWidget(
            right_manual,
            1,
        )

        return panel

    def create_manual_panel(
        self,
        title,
        buttons,
    ):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        layout.setSpacing(10)

        title_label = QLabel(title)

        title_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title_label
        )

        buttons_grid = self.create_buttons_grid(
            buttons
        )

        layout.addLayout(
            buttons_grid
        )

        layout.addStretch()

        return panel

    def create_buttons_grid(
        self,
        bayan_buttons,
    ):
        """
        Create bayan buttons in five vertical columns.

        Visual order from left to right:

            physical row 2 -> visual row 1
            physical row 1 -> visual row 2
            physical row 3 -> visual row 3
            physical row 4 -> visual row 4
            physical row 5 -> visual row 5

        Visual rows 2 and 4 are shifted upward
        by half a button step to reproduce the
        diagonal / staggered bayan keyboard.
        """

        grid = QGridLayout()

        grid.setHorizontalSpacing(6)

        # Small vertical spacing keeps the keyboard compact.
        grid.setVerticalSpacing(2)

        grid.setAlignment(
            Qt.AlignTop
            | Qt.AlignHCenter
        )

        # Physical row -> visible column.
        #
        # Rows 1 and 2 are intentionally swapped
        # to match our reference five-row B-griff layout.
        column_map = {
            1: 1,
            2: 0,
            3: 2,
            4: 3,
            5: 4,
        }

        for fallback_index, button in enumerate(
            bayan_buttons
        ):
            widget = BayanButtonWidget(
                button
            )

            widget.setFixedSize(
                30,
                30,
            )

            self.button_widgets[
                button.id
            ] = widget

            widget.pressed.connect(
                lambda b=button:
                self.engine.press_button(b)
            )

            widget.released.connect(
                lambda b=button:
                self.engine.release_button(b)
            )

            physical_row = (
                button.row
                if button.row is not None
                else 1
            )

            index = (
                button.index
                if button.index is not None
                else fallback_index
            )

            grid_column = column_map.get(
                physical_row,
                physical_row - 1,
            )

            # Every next button uses two logical rows.
            #
            # This gives us an intermediate logical row
            # that can be used for half-step staggering.
            #
            # Visible columns 2 and 4:
            #     start at logical row 0
            #
            # Visible columns 1, 3 and 5:
            #     start at logical row 1
            #
            # Result:
            #
            #       ○         ○
            #    ○     ○   ○
            #       ○         ○
            #    ○     ○   ○
            #
            # i.e. the characteristic diagonal layout.
            if grid_column in (1, 3):
                vertical_offset = 0
            else:
                vertical_offset = 1

            grid_row = (
                index * 2
                + vertical_offset
            )

            grid.addWidget(
                widget,
                grid_row,
                grid_column,
                Qt.AlignCenter,
            )

        return grid

    def create_bottom_panel(self):
        panel = QWidget()
        layout = QVBoxLayout(panel)

        title_label = QLabel(
            "MIDI Monitor"
        )

        title_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title_label
        )

        self.midi_monitor = MidiMonitor()

        self.midi_monitor.setReadOnly(
            True
        )

        self.midi_monitor.setMaximumHeight(
            140
        )

        layout.addWidget(
            self.midi_monitor
        )

        clear_btn = QPushButton(
            "Clear"
        )

        clear_btn.clicked.connect(
            self.midi_monitor.clear
        )

        layout.addWidget(
            clear_btn
        )

        return panel

    def setup_connections(self):
        self.engine.subscribe(
            self.midi_monitor.handle_event
        )

    def update_midi_ports(self):
        ports = self.midi_output.list_ports()

        self.midi_combo.clear()

        if not ports:
            self.midi_combo.addItem(
                "No MIDI outputs found"
            )

            self.connect_btn.setEnabled(
                False
            )

            self.status_label.setText(
                "Status: No MIDI outputs"
            )

            return

        self.midi_combo.addItems(
            ports
        )

        self.connect_btn.setEnabled(
            True
        )

        if len(ports) == 1:
            self.midi_combo.setCurrentIndex(
                0
            )

        if not self.midi_output.is_open:
            self.status_label.setText(
                "Status: Not connected"
            )

    def connect_midi(self):
        selected_port = (
            self.midi_combo.currentText()
        )

        if (
            not selected_port
            or selected_port
            == "No MIDI outputs found"
        ):
            return

        try:
            self.midi_output.open_port(
                selected_port
            )

            self.status_label.setText(
                f"Status: Connected — "
                f"{selected_port}"
            )

        except Exception as exc:
            self.status_label.setText(
                f"Status: MIDI Error: "
                f"{exc}"
            )

    def closeEvent(self, event):
        self.engine.all_notes_off()
        self.midi_output.close()

        event.accept()

    def sizeHint(self):
        return QSize(
            1200,
            750,
        )