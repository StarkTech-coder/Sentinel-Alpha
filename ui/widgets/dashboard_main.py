import sys
import os
import json
import random  # Rastgele veri üretimi için eklendi
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget, QTextEdit
from PyQt6.QtCore import Qt, QTimer  # Zamanlayıcı için QTimer eklendi
from ui.widgets.vision_widget import VisionWidget
from ui.widgets.health_widget import HealthWidget
from ui.widgets.acoustic_widget import AcousticWidget
from bridge.ui_bridge import UIBridge

# --- KRİTİK PATH AYARI ---
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
if project_root not in sys.path:
    sys.path.insert(0, project_root)


class SentinelDashboard(QMainWindow):
    def __init__(self):
        super().__init__()

        # --- PENCERE AYARLARI ---
        self.setWindowTitle("SENTINEL ALPHA - PENTAGON HUD v2.0 [GREEN-OPS MODE]")
        self.resize(1400, 900)
        self.setStyleSheet(
            "background-color: #050505; color: #00FF41; font-family: 'Courier New';"
        )

        # --- ANA LAYOUT KURULUMU ---
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QGridLayout(self.central_widget)

        # --- WIDGET ENTEGRASYONU ---
        self.vision_view = VisionWidget()
        self.health_view = HealthWidget()
        self.acoustic_view = AcousticWidget()
        self.system_integrity_panel = QTextEdit()
        self.target_data = QTextEdit()
        self.threat_scan_panel = QTextEdit()  # Sağ Orta: Canlı Panel
        self.brain_stream = QTextEdit()

        # --- STİL DÜZENLEMELERİ ---
        self._apply_styles()

        # --- GRID YERLEŞİMİ ---
        self.layout.addWidget(self.health_view, 0, 0)
        self.layout.addWidget(self.system_integrity_panel, 1, 0, 2, 1)
        self.layout.addWidget(self.acoustic_view, 3, 0)
        self.layout.addWidget(self.vision_view, 0, 1, 4, 1)
        self.layout.addWidget(self.target_data, 0, 2)
        self.layout.addWidget(self.threat_scan_panel, 1, 2, 2, 1)
        self.layout.addWidget(self.brain_stream, 3, 2)

        self.layout.setColumnStretch(0, 1)
        self.layout.setColumnStretch(1, 4)
        self.layout.setColumnStretch(2, 1)

        # --- SİNYAL KÖPRÜSÜ & VERİ YÜKLEME ---
        self.setup_bridge()
        self._load_static_integrity_data()

        # --- CANLI TEHDİT TARAYICI BAŞLATICI ---
        self.threat_timer = QTimer()
        self.threat_timer.timeout.connect(self._update_live_threat_scan)
        self.threat_timer.start(800)  # Her 0.8 saniyede bir güncelle

    def _apply_styles(self):
        text_style = """
            border: 2px solid #00FF41; 
            background: rgba(0, 255, 65, 0.05); 
            font-size: 10px; 
            color: #00FF41;
            font-weight: bold;
            line-height: 1.4;
        """
        widgets = [
            self.target_data,
            self.brain_stream,
            self.system_integrity_panel,
            self.threat_scan_panel,
        ]
        for w in widgets:
            w.setReadOnly(True)
            w.setStyleSheet(text_style)
            if w not in [self.system_integrity_panel, self.threat_scan_panel]:
                w.setPlaceholderText("WAITING FOR DATA STREAM...")

    def _load_static_integrity_data(self):
        content = (
            "--- SYSTEM INTEGRITY ---\nAUTH_USER: BHT-SENTINEL\nSECURITY_LEVEL: ALPHA-5\n"
            "ACCESS: GRANTED\nENCRYPTION: RSA-4096\n------------------------\n\n"
            "--- SECURITY PROTOCOL ---\nENCRYPTION: AES-256-GCM\nSSL/TLS: v1.3 ACTIVE\n"
            "FIREWALL: SENTINEL_SHIELD_V4\nSTATUS: SECURE / NO_INTRUSION\n\n"
            "--- LOCAL AI ENGINE ---\nCORE_ENGINE: OLLAMA / LLAMA-3.1\n"
            "QUANTIZATION: Q4_K_M\nINF_SPEED: 42.5 t/s\nLATENCY: 12ms\n\n"
            "--- NETWORK ACTIVITY ---\nLOCAL_IP: 192.168.1.XX\nPORT: 11434 (ACTIVE)\n"
            "UPLINK: STABLE\nLOSS: 0.00%"
        )
        self.system_integrity_panel.setText(content)

    def _update_live_threat_scan(self):
        """Sağ orta paneli canlı verilerle sürekli günceller."""
        freq = random.uniform(400.0, 2400.0)
        alt = random.randint(10000, 45000)
        mach = random.uniform(0.8, 2.5)
        sectors = ["ALPHA", "BRAVO", "CHARLIE", "DELTA", "ECHO"]

        content = (
            "--- LIVE THREAT & FREQ SCAN ---\n"
            f"SCAN_FREQ: {freq:.3f} MHz\n"
            f"RADAR_STATUS: SCANNING {random.choice(['[|]', '[/]', '[-]', '[\\\\]'])}\n"
            "--------------------------\n"
            f"[!] OBJ_ID: SENTINEL-{random.randint(100,999)}\n"
            f"    ALTITUDE: {alt:,} FT\n"
            f"    VELOCITY: MACH {mach:.2f}\n"
            f"    THREAT: {'HIGH' if mach > 1.5 else 'MODERATE'}\n"
            "--------------------------\n"
            f"[+] SIG_TYPE: {random.choice(['PULSE', 'BURST', 'ENCRYPTED'])}\n"
            f"    ORIGIN: SECTOR_{random.choice(sectors)}-{random.randint(1,9)}\n"
            "--------------------------\n"
            f"ENCRYPT_KEY: 0x{random.randint(1000,9999)}AB\n"
            f"SIGNAL_STRENGTH: -{random.randint(40,90)} dBm"
        )
        self.threat_scan_panel.setText(content)

    def setup_bridge(self):
        try:
            self.bridge = UIBridge()
            self.bridge.vision_signal.connect(self.vision_view.update_frame)
            self.bridge.health_signal.connect(self.health_view.update_status)
            self.bridge.metadata_signal.connect(self.update_metadata_panel)
            self.bridge.acoustic_signal.connect(self.acoustic_view.update_waveform)
            self.bridge.start()
        except Exception as e:
            print(f"[ERROR] Bridge başlatılamadı: {e}")

    def update_metadata_panel(self, data):
        try:
            if "[SENTINEL_INTEL]" in data:
                analysis = data["[SENTINEL_INTEL]"]
                self.brain_stream.append(f"> INTEL REPORT:\n{analysis}\n---")
                scroll_brain = self.brain_stream.verticalScrollBar()
                scroll_brain.setValue(scroll_brain.maximum())
            else:
                formatted_data = json.dumps(data, indent=2)
                self.target_data.append(f"-> [INCOMING EVENT]:\n{formatted_data}\n")
                scroll_bar = self.target_data.verticalScrollBar()
                scroll_bar.setValue(scroll_bar.maximum())
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
