import psutil
import zmq
import time
import random
from datetime import datetime


def run_system_agent():
    # 1. ZMQ KURULUMU
    context = zmq.Context()
    # ARTIK PUSH: Veriyi merkeze itiyoruz
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5555")  # Master Router Giriş Portu

    print("[SYSTEM_AGENT] M2 Telemetri Ajanı (CPU/GPU/ANE) aktif. Santrale bağlandı.")

    while True:
        # Gerçek CPU verisi
        cpu = psutil.cpu_percent(interval=None)

        # M2 GPU ve ANE simülasyonu
        # VisionAgent (YOLO) çalışırken GPU ve ANE yükü doğal olarak artar
        gpu_sim = cpu * 1.2 if cpu > 15 else random.uniform(5, 12)
        ane_sim = random.uniform(40, 75) if cpu > 30 else random.uniform(2, 8)

        # 2. SANTAL VE WIDGET UYUMLU PAYLOAD
        payload = {
            "agent": "SystemAgent",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "metadata": {
                "cpu_load": cpu,
                "gpu_load": round(gpu_sim, 1),
                "ane_load": round(ane_sim, 1),
                "status": "OPERATIONAL",
            },
        }

        # Veriyi Santrale fırlat
        socket.send_json(payload)

        # Loglama
        print(
            f"[{payload['timestamp']}] [SYSTEM] CPU: {cpu}% | GPU: {gpu_sim:.1f}% | ANE: {ane_sim:.1f}%"
        )

        # 0.5 saniye bekleme idealdir, sistemi yormaz
        time.sleep(0.5)


if __name__ == "__main__":
    run_system_agent()
