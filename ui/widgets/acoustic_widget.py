import zmq
import json
import random
from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, QTimer


class AcousticWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.wave_history = [" " for _ in range(30)]

        # STARK/SENTINEL STİLİ
        self.setStyleSheet("""
            border: 2px solid #00FF41; 
            background: rgba(0, 255, 65, 0.05); 
            font-size: 12px; 
            font-family: 'Courier New';
            color: #00FF41;
            font-weight: bold;
        """)

        # ZMQ BAĞLANTISI (SUB - Abone Telsizi)
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        # Master Router'ın ÇIKIŞ (Publisher) portuna bağlanıyoruz
        self.subscriber.connect("tcp://localhost:5558")
        # Boş string ("") her şeyi dinle demek, ama biz içerde ayıklayacağız
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # Telsizi dinlemek için Timer (Arayüzü dondurmaz)
        self.network_timer = QTimer()
        self.network_timer.timeout.connect(self.check_network)
        self.network_timer.start(10)  # 10ms'de bir telsize bak

    def check_network(self):
        """Telsizden yeni bir paket gelmiş mi diye bakar."""
        try:
            # NOBLOCK sayesinde veri yoksa beklemez, hemen geçer
            message = self.subscriber.recv_json(flags=zmq.NOBLOCK)

            # Sadece AcousticAgent'tan gelen verilerle ilgilen
            if message.get("agent") == "AcousticAgent":
                metadata = message.get("metadata", {})
                # Ajanın gönderdiği ses seviyesini al (yoksa 0.0)
                level = metadata.get("db_level", 0.0)
                self.update_waveform(level)

        except zmq.Again:
            # Henüz yeni bir mesaj gelmediğinde buraya düşer, sorun yok.
            pass
        except Exception as e:
            print(f"[ACOUSTIC_WIDGET] Hata: {e}")

    def update_waveform(self, level):
        """Veriyi HUD formatında ekrana basar."""
        chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        idx = int(min(level / 12.5, 8))
        current_char = chars[idx]

        self.wave_history.pop(0)
        self.wave_history.append(current_char)
        wave_str = "".join(self.wave_history)

        db_val = -(100 - level) / 2

        self.setPlainText(
            f"--- ACOUSTIC MONITOR ---\n"
            f"REF: SIG-INTEL-ALPHA\n\n"
            f"INTENSITY: %{level:.1f}\n"
            f"SPECTRUM:  {db_val:.1f} dB\n"
            f"WAVEFORM:  [{wave_str}]\n\n"
            f"STATUS: {'[ ANALYZING ]' if level < 70 else '[ TARGET DETECTED ]'}"
        )

    def closeEvent(self, event):
        """Widget kapandığında telsizi de kapat."""
        self.subscriber.close()
        self.context.term()
        event.accept()
