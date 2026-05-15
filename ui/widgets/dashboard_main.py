import sys
import os
import json

# --- KRİTİK PATH AYARI ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# -------------------------

from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTextEdit
from PyQt6.QtCore import Qt
from ui.widgets.vision_widget import VisionWidget
from ui.widgets.health_widget import HealthWidget
from ui.widgets.acoustic_widget import AcousticWidget
from bridge.ui_bridge import UIBridge


class SentinelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SENTINEL ALPHA - PENTAGON HUD v2.0")
        self.resize(1400, 900)
        self.setStyleSheet(
            "background-color: #050505; color: #00FF41; font-family: 'Courier New';"
        )

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # Widgetlar
        self.vision_view = VisionWidget()
        self.health_view = HealthWidget()
        self.acoustic_view = AcousticWidget()
        self.system_integrity_panel = QTextEdit()
        self.target_data = QTextEdit()
        self.threat_scan_panel = QTextEdit()
        self.brain_stream = QTextEdit()

        self._apply_styles()

        # Grid Yerleşimi
        self.layout.addWidget(self.health_view, 0, 0)
        self.layout.addWidget(self.system_integrity_panel, 1, 0, 2, 1)
        self.layout.addWidget(self.acoustic_view, 3, 0)
        self.layout.addWidget(self.vision_view, 0, 1, 4, 1)
        self.layout.addWidget(self.target_data, 0, 2)
        self.layout.addWidget(self.threat_scan_panel, 1, 2, 2, 1)
        self.layout.addWidget(self.brain_stream, 3, 2)

        self.layout.setColumnStretch(1, 4)
        self.setup_bridge()

    def _apply_styles(self):
        text_style = "border: 2px solid #00FF41; background: rgba(0, 255, 65, 0.05); font-size: 10px; color: #00FF41;"
        for w in [
            self.target_data,
            self.brain_stream,
            self.system_integrity_panel,
            self.threat_scan_panel,
        ]:
            w.setReadOnly(True)
            w.setStyleSheet(text_style)

    def setup_bridge(self):
        """DÜZELTİLDİ: Sinyallerin widgetlar ile bağlantısı yapıldı."""
        try:
            self.bridge = UIBridge()

            # KRİTİK BAĞLANTILAR
            self.bridge.vision_signal.connect(
                self.vision_view.update_frame
            )  # Görüntü Sinyali
            self.bridge.health_signal.connect(
                self.health_view.update_metrics
            )  # Sistem Sağlığı
            self.bridge.acoustic_signal.connect(
                self.acoustic_view.update_level
            )  # Ses Seviyesi
            self.bridge.metadata_signal.connect(
                self.update_metadata_panel
            )  # Loglar ve AI

            self.bridge.start()
        except Exception as e:
            print(f"[ERROR] Bridge hatası: {e}")

    def update_metadata_panel(self, data):
        try:
            if "[SENTINEL_INTEL]" in data:
                analysis = data["[SENTINEL_INTEL]"]
                self.brain_stream.append(f"> INTEL REPORT:\n{analysis}\n---")
                self.brain_stream.verticalScrollBar().setValue(
                    self.brain_stream.verticalScrollBar().maximum()
                )
            else:
                formatted_data = json.dumps(data, indent=2)
                self.target_data.append(f"-> [INCOMING EVENT]:\n{formatted_data}\n")
                self.target_data.verticalScrollBar().setValue(
                    self.target_data.verticalScrollBar().maximum()
                )
        except Exception as e:
            print(f"[HUD_ERROR] Metadata update failed: {e}")

    def closeEvent(self, event):
        if hasattr(self, "bridge"):
            self.bridge.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SentinelDashboard()
    window.showMaximized()
    sys.exit(app.exec())
