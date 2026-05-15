from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt, QTimer
import random


class AcousticWidget(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        # Karakter bazlı dalga geçmişi (Sentinel stili)
        self.wave_history = [" " for _ in range(30)]

        # STARK/SENTINEL YEŞİLİ STİLİ (#00FF41)
        self.setStyleSheet("""
            border: 2px solid #00FF41; 
            background: rgba(0, 255, 65, 0.05); 
            font-size: 12px; 
            font-family: 'Courier New';
            color: #00FF41;
            font-weight: bold;
        """)
        self.setPlaceholderText("WAITING FOR ACOUSTIC DATA...")

        # Simülasyon için Timer (Gerçek veri gelmediğinde boş kalmasın)
        self.sim_timer = QTimer()
        self.sim_timer.timeout.connect(self.simulate_noise)
        self.sim_timer.start(100)  # 100ms hızında güncelle

    def simulate_noise(self):
        """Dron veya ortam sesi simülasyonu üretir."""
        # %0 - %100 arası rastgele yoğunluk
        fake_level = random.uniform(15.0, 45.0)
        # Bazen 'drone' yakalamış gibi peak yapsın
        if random.random() > 0.95:
            fake_level = random.uniform(80.0, 98.5)

        self.update_waveform(fake_level)

    def update_waveform(self, level):
        """
        Gelen seviyeyi karakter dalgasına ve dB verisine dönüştürür.
        level: 0.0 - 100.0 arası değer.
        """
        # Karakter seti (Düşükten yükseğe)
        chars = [" ", " ", "▂", "▃", "▄", "▅", "▆", "▇", "█"]
        idx = int(min(level / 12.5, 8))
        current_char = chars[idx]

        self.wave_history.pop(0)
        self.wave_history.append(current_char)
        wave_str = "".join(self.wave_history)

        # Desibel hesaplama simülasyonu (Level'ı dB formatına çekiyoruz)
        db_val = -(100 - level) / 2  # -50dB ile 0dB arası bir skala

        # HUD formatında metni bas
        self.setPlainText(
            f"--- ACOUSTIC MONITOR ---\n"
            f"REF: SIG-INTEL-ALPHA\n\n"
            f"INTENSITY: %{level:.1f}\n"
            f"SPECTRUM:  {db_val:.1f} dB\n"
            f"WAVEFORM:  [{wave_str}]\n\n"
            f"STATUS: {'[ ANALYZING ]' if level < 70 else '[ TARGET DETECTED ]'}"
        )

    def stop_simulation(self):
        """Gerçek AcousticAgent bağlandığında simülasyonu durdurmak için."""
        self.sim_timer.stop()
