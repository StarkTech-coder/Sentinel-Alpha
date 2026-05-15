import subprocess
import time
import sys
import os


def start_sentinel():
    print("\n" + "=" * 40)
    print("--- SENTINEL ALPHA - COMMAND CENTER ---")
    print("=" * 40 + "\n")

    base_dir = os.path.dirname(os.path.abspath(__file__))

    # --- ADIM 1: ÖNCE SANTRALİ (ROUTER) BAŞLAT ---
    # Santral tüm sistemin kalbi, o yüzden en başta o açılmalı.
    print("[1/3] Master Router başlatılıyor...")
    router = subprocess.Popen(
        [sys.executable, os.path.join(base_dir, "core/master_router.py")]
    )
    time.sleep(1.5)  # Santralin portları bağlaması için kısa bir es

    # --- ADIM 2: AJANLARI VE BEYNİ BAŞLAT ---
    print("[2/3] Sahadaki ajanlar ve AI modülü uyandırılıyor...")

    processes = {
        "Vision": os.path.join(base_dir, "agents/vision_agent.py"),
        "System": os.path.join(base_dir, "agents/system_agent.py"),
        "Acoustic": os.path.join(base_dir, "agents/acoustic_agent.py"),
        "Intelligence": os.path.join(base_dir, "agents/intelligence_agent.py"),
    }

    active_agents = []
    for name, path in processes.items():
        if os.path.exists(path):
            proc = subprocess.Popen([sys.executable, path])
            active_agents.append(proc)
            print(f"  > {name} Ajanı: AKTİF")
        else:
            print(f"  [!] UYARI: {name} dosyası bulunamadı: {path}")

    print("\n[3/3] HUD (Arayüz) yükleniyor. Sistem hazır!\n")
    time.sleep(2)

    # --- ADIM 3: ARAYÜZÜ BAŞLAT ---
    try:
        # Dashboard ana süreci kilitler (Dashboard kapanana kadar bekler)
        subprocess.run(
            [sys.executable, os.path.join(base_dir, "ui/widgets/dashboard_main.py")]
        )
    except KeyboardInterrupt:
        print("\n[STOP] Kullanıcı tarafından kapatma sinyali alındı.")
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Sistem hatası: {e}")
    finally:
        # GÜVENLİ KAPATMA (Cleanup)
        print("\n" + "-" * 40)
        print("[CLEANUP] Operasyon sonlandırılıyor...")

        # Router'ı kapat
        router.terminate()

        # Tüm ajanları tek tek kapat
        for agent in active_agents:
            agent.terminate()

        print("[SUCCESS] Tüm süreçler güvenli şekilde durduruldu.")
        print("-" * 40)


if __name__ == "__main__":
    start_sentinel()
