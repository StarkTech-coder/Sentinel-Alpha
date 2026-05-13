from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar


class HealthWidget(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.cpu_label = QLabel("SYSTEM HEALTH: M2 CORE")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setStyleSheet(
            "QProgressBar { border: 1px solid #00f2ff; text-align: center; color: #00f2ff; } "
            "QProgressBar::chunk { background-color: #00f2ff; }"
        )
        layout.addWidget(self.cpu_label)
        layout.addWidget(self.cpu_bar)
        self.setLayout(layout)

    def update_status(self, cpu_val):
        self.cpu_bar.setValue(int(cpu_val))
        self.cpu_label.setText(f"M2 CPU LOAD: %{cpu_val:.1f}")
