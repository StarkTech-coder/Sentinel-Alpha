import zmq
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt6.QtCore import Qt, QTimer


class HealthWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.layout.setSpacing(8)

        # --- SENTINEL YEŞİLİ HUD STİLİ ---
        self.hud_style = """
            QProgressBar {
                border: 2px solid #00FF41;
                border-radius: 0px;
                text-align: center;
                color: #000;
                background-color: rgba(0, 255, 65, 0.05);
                height: 18px;
                font-weight: bold;
                font-family: 'Courier New';
            }
            QProgressBar::chunk {
                background-color: #00FF41;
            }
            QLabel {
                color: #00FF41;
                font-family: 'Courier New';
                font-size: 11px;
                font-weight: bold;
                text-transform: uppercase;
            }
        """

        # --- CPU UNIT ---
        self.cpu_label = QLabel("M2 CPU CORE [ACTIVE]")
        self.cpu_bar = QProgressBar()

        # --- GPU UNIT ---
        self.gpu_label = QLabel("M2 GPU ENGINE [RENDERING]")
        self.gpu_bar = QProgressBar()

        # --- NEURAL ENGINE (ANE) UNIT ---
        self.ane_label = QLabel("APPLE NEURAL ENGINE [AI INFERENCE]")
        self.ane_bar = QProgressBar()

        self.setStyleSheet(self.hud_style)

        components = [
            (self.cpu_label, self.cpu_bar),
            (self.gpu_label, self.gpu_bar),
            (self.ane_label, self.ane_bar),
        ]

        for label, bar in components:
            bar.setRange(0, 100)
            bar.setValue(0)
            self.layout.addWidget(label)
            self.layout.addWidget(bar)
            self.layout.addSpacing(5)

        self.setLayout(self.layout)

        # --- ZMQ BAĞLANTISI (SUB - Abone) ---
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        # Master Router'ın çıkış portuna (Publisher) bağlanıyoruz
        self.subscriber.connect("tcp://localhost:5558")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # Telsizi dinlemek için Timer (Arayüzü dondurmaz)
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.check_network)
        self.network_timer.start(50)  # Donanım verileri için 50ms idealdir

    def check_network(self):
        """Master Router'dan gelen sistem verilerini yakalar."""
        try:
            # NOBLOCK: Veri yoksa bekleme, akışı bozma
            message = self.subscriber.recv_json(flags=zmq.NOBLOCK)

            # Sadece SystemAgent verilerini ayıkla
            if message.get("agent") == "SystemAgent":
                metadata = message.get("metadata", {})

                # Verileri sözlük yapısına çevirip update_status'a gönder
                metrics = {
                    "cpu": metadata.get("cpu_load", 0.0),
                    "gpu": metadata.get("gpu_load", 0.0),
                    "ane": metadata.get("ane_usage", 0.0),  # ANE verisi varsa
                }
                self.update_status(metrics)

        except zmq.Again:
            pass  # Yeni mesaj yok, devam et
        except Exception as e:
            print(f"[HEALTH_WIDGET] Telsiz Hatası: {e}")

    def update_status(self, metrics):
        """Gelen veriyi HUD barlarına yansıtır."""
        cpu_val = metrics.get("cpu", 0)
        gpu_val = metrics.get("gpu", 0)
        ane_val = metrics.get("ane", 0)

        self.cpu_bar.setValue(int(cpu_val))
        self.cpu_label.setText(f"M2 CPU LOAD: %{cpu_val:.1f}")

        self.gpu_bar.setValue(int(gpu_val))
        self.gpu_label.setText(f"M2 GPU LOAD: %{gpu_val:.1f}")

        self.ane_bar.setValue(int(ane_val))
        self.ane_label.setText(f"NEURAL ENGINE: %{ane_val:.1f}")

        self._apply_dynamic_color(self.cpu_bar, cpu_val)
        self._apply_dynamic_color(self.gpu_bar, gpu_val)
        self._apply_dynamic_color(self.ane_bar, ane_val)

    def _apply_dynamic_color(self, bar, value):
        if value > 95:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #FFA500; }")
        else:
            bar.setStyleSheet("QProgressBar::chunk { background-color: #00FF41; }")

    def closeEvent(self, event):
        """Kapatırken telsiz hatlarını temizle."""
        self.subscriber.close()
        self.context.term()
        event.accept()
