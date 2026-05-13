import sys
import json
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTextEdit
from PyQt6.QtCore import Qt
from ui.widgets.vision_widget import VisionWidget
from ui.widgets.health_widget import HealthWidget
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
        self.vision_view = VisionWidget()  # [1] MERKEZ: YOLO Canlı Akış
        self.health_view = HealthWidget()  # [5] SOL ÜST: M2 Telemetri
        self.target_data = QTextEdit()  # [4] SAĞ ÜST: Metadata (JSON Log)
        self.brain_stream = QTextEdit()  # [3] SAĞ ALT: Ollama Karar Akışı
        self.acoustic_view = QTextEdit()  # [2] SOL ALT: Akustik Sinyal Verisi

        # --- STİL DÜZENLEMELERİ ---
        self._apply_styles()

        # --- GRID YERLEŞİMİ (Pentagon/Heksagon Hibrit Düzen) ---
        # (row, col, row_span, col_span)
        self.layout.addWidget(self.health_view, 0, 0)  # Sol Üst
        self.layout.addWidget(self.acoustic_view, 1, 0)  # Sol Alt
        self.layout.addWidget(self.vision_view, 0, 1, 2, 1)  # MERKEZ (Geniş Panel)
        self.layout.addWidget(self.target_data, 0, 2)  # Sağ Üst
        self.layout.addWidget(self.brain_stream, 1, 2)  # Sağ Alt

        # Sütun oranlarını ayarla (Merkez panel her zaman odak noktasıdır)
        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 1)

        # --- SİNYAL KÖPRÜSÜ (ZMQ CONNECTION) ---
        self.setup_bridge()

    def _apply_styles(self):
        """Metin kutularına Stark HUD estetiği uygular."""
        text_style = """
            border: 1px solid #00f2ff; 
            background: rgba(0, 242, 255, 0.05); 
            font-size: 11px; 
            color: #00f2ff;
        """
        for w in [self.target_data, self.brain_stream, self.acoustic_view]:
            w.setReadOnly(True)
            w.setStyleSheet(text_style)
            w.setPlaceholderText("WAITING FOR DATA STREAM...")

    def setup_bridge(self):
        """UIBridge ile ZMQ kanallarını widget'lara bağlar."""
        self.bridge = UIBridge()

        # Sinyalleri ilgili fonksiyonlara bağla
        self.bridge.vision_signal.connect(self.vision_view.update_frame)
        self.bridge.health_signal.connect(self.health_view.update_status)
        self.bridge.metadata_signal.connect(self.update_metadata_panel)

        # Köprüyü ayrı bir thread olarak başlat
        self.bridge.start()

    def update_metadata_panel(self, data):
        """Sağ üstteki Metadata kutusuna canlı JSON verisini basar."""
        try:
            formatted_data = json.dumps(data, indent=2)
            self.target_data.append(f"-> [INCOMING EVENT]:\n{formatted_data}\n")

            # Otomatik aşağı kaydır (Auto-scroll)
            scroll_bar = self.target_data.verticalScrollBar()
            scroll_bar.setValue(scroll_bar.maximum())

            # Eğer Brain/Ollama mesajı varsa onu ayır ve Beyin kutusuna gönder
            if data.get("agent") == "BrainAgent":  # İleride eklenecek
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
    window.showMaximized()  # M2 ekranda tam ekran başlat
    sys.exit(app.exec())
