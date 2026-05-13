import subprocess
import time
import sys
import os


def start_sentinel():
    print("--- SENTINEL ALPHA BAŞLATILIYOR ---")
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. Ajanları ve Beyni başlat (Arka planda)
    # Yeni Acoustic Agent eklendi
    vision = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "agents/vision_agent.py")]
    )
    system = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "agents/system_agent.py")]
    )
    acoustic = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "agents/acoustic_agent.py")]
    )
    router = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "core/master_router.py")]
    )

    print("[INFO] Ajanlar arkada çalışıyor. HUD açılıyor...")
    time.sleep(3)

    # 2. Arayüzü başlat
    try:
        subprocess.run(
            [sys.executable, os.path.join(base_dir, "ui/widgets/dashboard_main.py")]
        )
    except KeyboardInterrupt:
        print("\n[STOP] Sistem kapatılıyor...")
    finally:
        # Tüm süreçleri güvenli şekilde kapat
        vision.terminate()
        system.terminate()
        acoustic.terminate()
        router.terminate()
        print("[CLEANUP] Tüm süreçler sonlandırıldı.")


if __name__ == "__main__":
    start_sentinel()
