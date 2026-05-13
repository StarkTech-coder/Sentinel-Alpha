import subprocess
import time
import sys
import os


def start_sentinel():
    print("--- SENTINEL ALPHA BAŞLATILIYOR ---")

    # Çalışma dizinini doğrula
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Ajanları ve Beyni başlat (Arka planda)
    vision = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "agents/vision_agent.py")]
    )
    system = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "agents/system_agent.py")]
    )
    router = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "core/master_router.py")]
    )

    print("[INFO] Ajanlar arkada çalışıyor. HUD açılıyor...")
    time.sleep(3)  # CoreML ve ZMQ kurulumu için süre

    # 2. Arayüzü başlat (Yeni Pentagon Dashboard yolu)
    try:
        # Dashboard artık ui/widgets altında değil, direkt ui/ içinde
        subprocess.run([sys.executable, os.path.join(base_dir, "ui/dashboard_main.py")])
    except KeyboardInterrupt:
        print("\n[STOP] Sistem kapatılıyor...")
    finally:
        # Kapatırken tüm süreçleri temizle
        vision.terminate()
        system.terminate()
        router.terminate()
        print("[CLEANUP] Tüm süreçler sonlandırıldı.")


if __name__ == "__main__":
    start_sentinel()
