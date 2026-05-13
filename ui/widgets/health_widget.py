from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt


class HealthWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)  # Barlar arası boşluk

        # --- Stil Tanımı ---
        self.hud_style = """
            QProgressBar {
                border: 1px solid #00f2ff;
                border-radius: 2px;
                text-align: center;
                color: #00f2ff;
                background-color: rgba(0, 242, 255, 0.05);
                height: 15px;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #00f2ff;
            }
            QLabel {
                color: #00f2ff;
                font-family: 'Courier New';
                font-size: 12px;
                text-transform: uppercase;
            }
        """

        # --- CPU Bölümü ---
        self.cpu_label = QLabel("SYSTEM HEALTH: M2 CORE")
        self.cpu_bar = QProgressBar()
        self.cpu_bar.setRange(0, 100)
        self.cpu_bar.setValue(0)

        # --- RAM Bölümü ---
        self.ram_label = QLabel("MEMORY ALLOCATION: LPDDR5")
        self.ram_bar = QProgressBar()
        self.ram_bar.setRange(0, 100)
        self.ram_bar.setValue(0)

        # Stilleri Uygula
        self.setStyleSheet(self.hud_style)

        # Layout'a Ekle
        self.layout.addWidget(self.cpu_label)
        self.layout.addWidget(self.cpu_bar)
        self.layout.addSpacing(5)  # İki bar arası ekstra boşluk
        self.layout.addWidget(self.ram_label)
        self.layout.addWidget(self.ram_bar)

        self.setLayout(self.layout)

    def update_status(self, cpu_val, ram_val):
        """
        UIBridge'den gelen verileri barlara yansıtır.
        """
        # CPU Güncelleme
        self.cpu_bar.setValue(int(cpu_val))
        self.cpu_label.setText(f"M2 CPU LOAD: %{cpu_val:.1f}")

        # RAM Güncelleme
        self.ram_bar.setValue(int(ram_val))
        self.ram_label.setText(f"RAM USAGE: %{ram_val:.1f}")

        # Kritik Durum Renk Değişimi (Opsiyonel: %90 üzeri kırmızımsı efekt)
        if cpu_val > 90:
            self.cpu_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #ff4444; }"
            )
        else:
            self.cpu_bar.setStyleSheet(
                "QProgressBar::chunk { background-color: #00f2ff; }"
            )
