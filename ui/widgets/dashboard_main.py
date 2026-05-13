import sys
import os
import json

# --- KRİTİK PATH AYARI ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTextEdit
from PyQt6.QtCore import Qt
from ui.widgets.vision_widget import VisionWidget
from ui.widgets.health_widget import HealthWidget
from ui.widgets.acoustic_widget import AcousticWidget  # YENİ EKLEME
from bridge.ui_bridge import UIBridge


class SentinelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- PENCERE AYARLARI ---
        self.setWindowTitle("SENTINEL ALPHA - PENTAGON HUD v2.0")
        self.resize(1400, 900)
        self.setStyleSheet(
            "background-color: #050505; color: #00f2ff; font-family: 'Courier New';"
        )

        # --- ANA LAYOUT KURULUMU ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # --- WIDGET ENTEGRASYONU ---
        self.vision_view = VisionWidget()
        self.health_view = HealthWidget()
        self.target_data = QTextEdit()
        self.brain_stream = QTextEdit()
        self.acoustic_view = AcousticWidget()  # DÜZELTİLDİ: Özel widget kullanılıyor

        # --- STİL DÜZENLEMELERİ ---
        self._apply_styles()

        # --- GRID YERLEŞİMİ ---
        self.layout.addWidget(self.health_view, 0, 0)
        self.layout.addWidget(self.acoustic_view, 1, 0)
        self.layout.addWidget(self.vision_view, 0, 1, 2, 1)
        self.layout.addWidget(self.target_data, 0, 2)
        self.layout.addWidget(self.brain_stream, 1, 2)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 1)

        # --- SİNYAL KÖPRÜSÜ ---
        self.setup_bridge()

    def _apply_styles(self):
        """Metin kutularına Stark HUD estetiği uygular."""
        text_style = """
            border: 1px solid #00f2ff; 
            background: rgba(0, 242, 255, 0.05); 
            font-size: 11px; 
            color: #00f2ff;
        """
        for w in [
            self.target_data,
            self.brain_stream,
        ]:  # acoustic_view zaten kendi içinde stillendi
            w.setReadOnly(True)
            w.setStyleSheet(text_style)
            w.setPlaceholderText("WAITING FOR DATA STREAM...")

    def setup_bridge(self):
        """UIBridge ile ZMQ kanallarını widget'lara bağlar."""
        self.bridge = UIBridge()

        # Sinyalleri bağla
        self.bridge.vision_signal.connect(self.vision_view.update_frame)
        self.bridge.health_signal.connect(self.health_view.update_status)
        self.bridge.metadata_signal.connect(self.update_metadata_panel)

        # DÜZELTİLDİ: Sinyal artık AcousticWidget'ın kendi fonksiyonuna gidiyor
        self.bridge.acoustic_signal.connect(self.acoustic_view.update_waveform)

        self.bridge.start()

    def update_metadata_panel(self, data):
        """Sağ üstteki Metadata kutusuna canlı JSON verisini basar."""
        try:
            formatted_data = json.dumps(data, indent=2)
            self.target_data.append(f"-> [INCOMING EVENT]:\n{formatted_data}\n")
            scroll_bar = self.target_data.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

            if data.get("agent") == "BrainAgent":
                self.brain_stream.append(f"> STRATEGY: {data.get('comment')}")
        except Exception as e:
            print(f"[HUD_ERROR] Metadata update failed: {e}")

    def closeEvent(self, event):
        """Pencere kapandığında köprüyü güvenli durdur."""
        self.bridge.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SentinelDashboard()
    window.showMaximized()
    sys.exit(app.exec())
