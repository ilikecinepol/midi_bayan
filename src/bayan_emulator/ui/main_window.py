"""
Main window for Bayan MIDI Emulator GUI.
"""

from PySide6.QtCore import Qt, QSize, QEvent
from PySide6.QtWidgets import (
    QApplication,
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

from bayan_emulator.engine.bayan_engine import BayanEngine
from bayan_emulator.layout_generators.b_griff import create_b_griff_config
from bayan_emulator.midi.output import MidiOutputService
from bayan_emulator.models.layout import BayanLayout
from bayan_emulator.ui.bayan_button import BayanButtonWidget
from bayan_emulator.ui.midi_monitor import MidiMonitor


# ============================================================
# General MIDI instruments
# ============================================================

GM_INSTRUMENTS = (
    ("Баян / Accordion", 21),
    ("Harmonica", 22),
    ("Tango Accordion", 23),
    ("Фортепиано", 0),
    ("Bright Piano", 1),
    ("Electric Piano", 4),
    ("Church Organ", 19),
    ("Reed Organ", 20),
    ("Strings", 48),
    ("Synth Strings", 50),
)


# ============================================================
# PC keyboard
# ============================================================

# First PC key = MIDI 45 = A2
PC_KEYBOARD_BASE_MIDI = 45


# Windows hardware scan codes.
#
# This makes the bayan keyboard independent from
# EN / RU keyboard layout.
#
# Physical pattern:
#
# Q W E R T Y U I O P
# A S D F G H J K L ;
# Z X C V B N M , . /
#
# We read it vertically:
#
# Q -> A2
# A -> A#2
# Z -> B2
# W -> C3
# S -> C#3
# X -> D3
# ...

PC_KEYBOARD_BINDINGS = (
    # scan code, Qt key, display name

    (16, Qt.Key.Key_Q, "Q"),
    (30, Qt.Key.Key_A, "A"),
    (44, Qt.Key.Key_Z, "Z"),

    (17, Qt.Key.Key_W, "W"),
    (31, Qt.Key.Key_S, "S"),
    (45, Qt.Key.Key_X, "X"),

    (18, Qt.Key.Key_E, "E"),
    (32, Qt.Key.Key_D, "D"),
    (46, Qt.Key.Key_C, "C"),

    (19, Qt.Key.Key_R, "R"),
    (33, Qt.Key.Key_F, "F"),
    (47, Qt.Key.Key_V, "V"),

    (20, Qt.Key.Key_T, "T"),
    (34, Qt.Key.Key_G, "G"),
    (48, Qt.Key.Key_B, "B"),

    (21, Qt.Key.Key_Y, "Y"),
    (35, Qt.Key.Key_H, "H"),
    (49, Qt.Key.Key_N, "N"),

    (22, Qt.Key.Key_U, "U"),
    (36, Qt.Key.Key_J, "J"),
    (50, Qt.Key.Key_M, "M"),

    (23, Qt.Key.Key_I, "I"),
    (37, Qt.Key.Key_K, "K"),
    (51, Qt.Key.Key_Comma, ","),

    (24, Qt.Key.Key_O, "O"),
    (38, Qt.Key.Key_L, "L"),
    (52, Qt.Key.Key_Period, "."),

    (25, Qt.Key.Key_P, "P"),
    (39, Qt.Key.Key_Semicolon, ";"),
    (53, Qt.Key.Key_Slash, "/"),
)


class MainWindow(QMainWindow):
    """Main window with bayan interface and MIDI controls."""

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bayan MIDI Emulator")
        self.resize(1200, 750)
        self.setMinimumSize(900, 600)

        # Let the window receive keyboard input.
        self.setFocusPolicy(
            Qt.FocusPolicy.StrongFocus
        )

        self.engine = BayanEngine()
        self.midi_output = MidiOutputService()

        self.button_widgets: dict[
            str,
            BayanButtonWidget
        ] = {}

        # Keyboard bindings.
        self._computer_scan_bindings = {}
        self._computer_qt_bindings = {}

        # Contains identifiers of currently held
        # physical PC keys.
        self._pressed_computer_keys = set()

        layout_config = create_b_griff_config()
        self.layout = BayanLayout(
            instrument=layout_config["instrument"],
            layout_name=layout_config["layout_name"],
            right_manual=layout_config["right_manual"],
            left_manual=layout_config["left_manual"],
        )

        # Engine -> MIDI.
        self.engine.subscribe(
            self.midi_output.handle_event
        )

        self.init_ui()
        self.setup_connections()
        self.setup_computer_keyboard()

    # ============================================================
    # UI
    # ============================================================

    def init_ui(self):
        central_widget = QWidget()

        self.setCentralWidget(
            central_widget
        )

        main_layout = QVBoxLayout(
            central_widget
        )

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

    # ============================================================
    # Top panel
    # ============================================================

    def create_top_panel(self):
        panel = QWidget()

        layout = QHBoxLayout(
            panel
        )

        layout.setSpacing(10)

        # --------------------------------------------------------
        # MIDI output
        # --------------------------------------------------------

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

        # --------------------------------------------------------
        # Instrument
        # --------------------------------------------------------

        layout.addWidget(
            QLabel("Тембр:")
        )

        self.instrument_combo = QComboBox()

        for name, program in GM_INSTRUMENTS:
            self.instrument_combo.addItem(
                name,
                program,
            )

        # Default = Accordion.
        self.instrument_combo.setCurrentIndex(
            0
        )

        self.instrument_combo.currentIndexChanged.connect(
            self.change_instrument
        )

        layout.addWidget(
            self.instrument_combo
        )

        # --------------------------------------------------------
        # Status
        # --------------------------------------------------------

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

    # ============================================================
    # Bayan panels
    # ============================================================

    def create_middle_panel(self):
        panel = QWidget()

        layout = QHBoxLayout(
            panel
        )

        layout.setSpacing(30)

        left_manual = (
            self.create_manual_panel(
                "LEFT MANUAL",
                self.layout.left_manual,
            )
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

        bellows.setMinimumWidth(
            80
        )

        layout.addWidget(
            bellows
        )

        right_manual = (
            self.create_manual_panel(
                "RIGHT MANUAL",
                self.layout.right_manual,
            )
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

        layout = QVBoxLayout(
            panel
        )

        layout.setSpacing(10)

        title_label = QLabel(
            title
        )

        title_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title_label
        )

        buttons_grid = (
            self.create_buttons_grid(
                buttons
            )
        )

        layout.addLayout(
            buttons_grid
        )

        layout.addStretch()

        return panel

    # ============================================================
    # Bayan button geometry
    # ============================================================

    def create_buttons_grid(
        self,
        bayan_buttons,
    ):
        """
        Create five vertical B-griff columns.

        Current visual order:

            physical row 2 -> visual column 1
            physical row 1 -> visual column 2
            physical row 3 -> visual column 3
            physical row 4 -> visual column 4
            physical row 5 -> visual column 5

        Columns 2 and 4 are shifted vertically,
        creating the diagonal B-griff geometry.
        """

        grid = QGridLayout()

        grid.setHorizontalSpacing(
            6
        )

        grid.setVerticalSpacing(
            2
        )

        grid.setAlignment(
            Qt.AlignTop
            | Qt.AlignHCenter
        )

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

            # ----------------------------------------------------
            # Mouse input
            # ----------------------------------------------------

            widget.pressed.connect(
                lambda b=button:
                self.engine.press_button(
                    b,
                    source="screen",
                )
            )

            widget.released.connect(
                lambda b=button:
                self.engine.release_button(
                    b,
                    source="screen",
                )
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

            grid_column = (
                column_map.get(
                    physical_row,
                    physical_row - 1,
                )
            )

            # Diagonal B-griff geometry.
            if grid_column in (
                1,
                3,
            ):
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

    # ============================================================
    # MIDI monitor
    # ============================================================

    def create_bottom_panel(self):
        panel = QWidget()

        layout = QVBoxLayout(
            panel
        )

        title_label = QLabel(
            "MIDI Monitor"
        )

        title_label.setAlignment(
            Qt.AlignCenter
        )

        layout.addWidget(
            title_label
        )

        self.midi_monitor = (
            MidiMonitor()
        )

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

    # ============================================================
    # Engine connections
    # ============================================================

    def setup_connections(self):
        self.engine.subscribe(
            self.midi_monitor.handle_event
        )

    # ============================================================
    # MIDI output
    # ============================================================

    def update_midi_ports(self):
        ports = (
            self.midi_output.list_ports()
        )

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
            program = (
                self.instrument_combo.currentData()
            )

            if program is not None:
                self.midi_output.set_program(
                    int(program)
                )

            self.midi_output.open_port(
                selected_port
            )

            instrument = (
                self.instrument_combo.currentText()
            )

            self.status_label.setText(
                f"Status: Connected — "
                f"{instrument}"
            )

            # Give focus back to the instrument
            # after clicking Connect.
            self.setFocus()

        except Exception as exc:
            self.status_label.setText(
                f"Status: MIDI Error: {exc}"
            )

    def change_instrument(
        self,
        index,
    ):
        if index < 0:
            return

        program = (
            self.instrument_combo.itemData(
                index
            )
        )

        if program is None:
            return

        try:
            self.midi_output.set_program(
                int(program)
            )

            if self.midi_output.is_open:
                instrument = (
                    self.instrument_combo.currentText()
                )

                self.status_label.setText(
                    f"Status: Connected — "
                    f"{instrument}"
                )

            # Return keyboard focus to bayan.
            self.setFocus()

        except Exception as exc:
            self.status_label.setText(
                f"Status: MIDI Error: {exc}"
            )

    # ============================================================
    # PC keyboard
    # ============================================================

    def setup_computer_keyboard(self):
        """
        Map the physical PC keyboard chromatically.

        Q -> A2
        A -> A#2
        Z -> B2

        W -> C3
        S -> C#3
        X -> D3

        etc.
        """

        note_to_button = {}

        # Only use primary B-griff rows.
        # Rows 4 and 5 duplicate pitches.
        for button in self.layout.right_manual:

            if button.row not in (
                1,
                2,
                3,
            ):
                continue

            for midi_note in button.midi_notes:
                note_to_button[
                    midi_note
                ] = button

        for offset, (
            scan_code,
            qt_key,
            key_name,
        ) in enumerate(
            PC_KEYBOARD_BINDINGS
        ):
            midi_note = (
                PC_KEYBOARD_BASE_MIDI
                + offset
            )

            button = (
                note_to_button.get(
                    midi_note
                )
            )

            if button is None:
                continue

            binding = (
                key_name,
                button,
            )

            # Primary mapping:
            # physical Windows key.
            self._computer_scan_bindings[
                scan_code
            ] = binding

            # Fallback mapping:
            # Qt logical key.
            self._computer_qt_bindings[
                int(qt_key)
            ] = binding

            widget = (
                self.button_widgets.get(
                    button.id
                )
            )

            if widget is not None:
                widget.setToolTip(
                    f"{button.label} — "
                    f"клавиша {key_name}"
                )

        app = QApplication.instance()

        if app is not None:
            app.installEventFilter(
                self
            )

    def get_keyboard_binding(
        self,
        event,
    ):
        """
        Resolve keyboard event.

        Prefer native hardware scan code.
        Fall back to Qt key code.
        """

        scan_code = int(
            event.nativeScanCode()
        )

        if scan_code:
            binding = (
                self._computer_scan_bindings.get(
                    scan_code
                )
            )

            if binding is not None:
                return (
                    ("scan", scan_code),
                    binding,
                )

        qt_key = int(
            event.key()
        )

        binding = (
            self._computer_qt_bindings.get(
                qt_key
            )
        )

        if binding is not None:
            return (
                ("qt", qt_key),
                binding,
            )

        return (
            None,
            None,
        )

    def eventFilter(
        self,
        watched,
        event,
    ):
        event_type = (
            event.type()
        )

        # --------------------------------------------------------
        # Window loses focus
        # --------------------------------------------------------

        if (
            watched is self
            and event_type
            == QEvent.Type.WindowDeactivate
        ):
            self.release_all_computer_keys()

        # --------------------------------------------------------
        # Only keyboard events below
        # --------------------------------------------------------

        if event_type not in (
            QEvent.Type.KeyPress,
            QEvent.Type.KeyRelease,
        ):
            return super().eventFilter(
                watched,
                event,
            )

        if not self.isActiveWindow():
            return super().eventFilter(
                watched,
                event,
            )

        # --------------------------------------------------------
        # Don't intercept Ctrl / Alt / Win shortcuts
        # --------------------------------------------------------

        modifiers = (
            event.modifiers()
        )

        if modifiers & (
            Qt.KeyboardModifier.ControlModifier
            | Qt.KeyboardModifier.AltModifier
            | Qt.KeyboardModifier.MetaModifier
        ):
            return super().eventFilter(
                watched,
                event,
            )

        # --------------------------------------------------------
        # Find key binding
        # --------------------------------------------------------

        key_id, binding = (
            self.get_keyboard_binding(
                event
            )
        )

        if (
            key_id is None
            or binding is None
        ):
            return super().eventFilter(
                watched,
                event,
            )

        # Windows key auto-repeat must not
        # create repeated NOTE_ON.
        if event.isAutoRepeat():
            return True

        key_name, button = binding

        widget = (
            self.button_widgets.get(
                button.id
            )
        )

        # --------------------------------------------------------
        # KEY DOWN
        # --------------------------------------------------------

        if (
            event_type
            == QEvent.Type.KeyPress
        ):
            if (
                key_id
                in self._pressed_computer_keys
            ):
                return True

            self._pressed_computer_keys.add(
                key_id
            )

            self.engine.press_button(
                button,
                source="computer_keyboard",
            )

            if widget is not None:
                widget.setDown(
                    True
                )

            return True

        # --------------------------------------------------------
        # KEY UP
        # --------------------------------------------------------

        if (
            key_id
            not in self._pressed_computer_keys
        ):
            return True

        self._pressed_computer_keys.remove(
            key_id
        )

        self.engine.release_button(
            button,
            source="computer_keyboard",
        )

        if widget is not None:
            widget.setDown(
                False
            )

        return True

    def release_all_computer_keys(self):
        """
        Release all PC-keyboard notes.

        Protects against stuck notes when the
        application loses focus.
        """

        for key_id in list(
            self._pressed_computer_keys
        ):
            key_type, code = key_id

            if key_type == "scan":
                binding = (
                    self._computer_scan_bindings.get(
                        code
                    )
                )
            else:
                binding = (
                    self._computer_qt_bindings.get(
                        code
                    )
                )

            if binding is None:
                continue

            _, button = binding

            self.engine.release_button(
                button,
                source="computer_keyboard",
            )

            widget = (
                self.button_widgets.get(
                    button.id
                )
            )

            if widget is not None:
                widget.setDown(
                    False
                )

        self._pressed_computer_keys.clear()

    # ============================================================
    # Close
    # ============================================================

    def closeEvent(
        self,
        event,
    ):
        self.release_all_computer_keys()

        app = QApplication.instance()

        if app is not None:
            app.removeEventFilter(
                self
            )

        self.engine.all_notes_off()
        self.midi_output.close()

        event.accept()

    def sizeHint(self):
        return QSize(
            1200,
            750,
        )
