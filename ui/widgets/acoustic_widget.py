from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt


class AcousticWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.wave_history = [" " for _ in range(30)]
        self.setStyleSheet("""
            border: 1px solid #00f2ff; 
            background: rgba(0, 242, 255, 0.05); 
            font-size: 11px; 
            color: #00f2ff;
        """)
        self.setPlaceholderText("WAITING FOR AUDIO STREAM...")

    def update_waveform(self, level):
        chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        idx = int(min(level / 12.5, 8))
        current_char = chars[idx]

        self.wave_history.pop(0)
        self.wave_history.append(current_char)
        wave_str = "".join(self.wave_history)

        self.setPlainText(
            f"--- ACOUSTIC MONITOR ---\n\n"
            f"INTENSITY: %{level:.1f}\n"
            f"WAVEFORM:  {wave_str}\n\n"
            f"STATUS: ACTIVE"
        )
