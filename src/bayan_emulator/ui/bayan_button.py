from PySide6.QtWidgets import QPushButton

from bayan_emulator.models.button import BayanButton


BLACK_PITCH_CLASSES = {
    1,   # C#
    3,   # D#
    6,   # F#
    8,   # G#
    10,  # A#
}


class BayanButtonWidget(QPushButton):

    def __init__(
        self,
        button_model: BayanButton,
        parent=None,
    ):
        super().__init__(parent)

        self.button_model = button_model

        self.setText(button_model.label)

        self.setFixedSize(30, 30)

        midi_note = button_model.midi_notes[0]

        is_black = (
            midi_note % 12
            in BLACK_PITCH_CLASSES
        )

        if is_black:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #171717;
                    color: white;

                    border: 1px solid #555555;
                    border-radius: 15px;

                    font-size: 8px;
                    font-weight: 600;
                }

                QPushButton:hover {
                    background-color: #333333;
                    border: 2px solid #aaaaaa;
                }

                QPushButton:pressed {
                    background-color: #d49a32;
                    color: black;
                    border: 2px solid #ffd36a;
                }
                """
            )

        else:
            self.setStyleSheet(
                """
                QPushButton {
                    background-color: #f1f1f1;
                    color: #111111;

                    border: 1px solid #999999;
                    border-radius: 15px;

                    font-size: 8px;
                    font-weight: 600;
                }

                QPushButton:hover {
                    background-color: #ffffff;
                    border: 2px solid #bbbbbb;
                }

                QPushButton:pressed {
                    background-color: #d49a32;
                    color: black;
                    border: 2px solid #ffd36a;
                }
                """
            )