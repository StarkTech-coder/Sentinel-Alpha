import psutil
import zmq
import time
import random
from datetime import datetime


def run_system_agent():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5557")

    print("[SYSTEM_AGENT] M2 Telemetri Ajanı (CPU/GPU/ANE) aktif. Port: 5557")

    while True:
        # Gerçek CPU verisi
        cpu = psutil.cpu_percent(interval=None)

        # M2 GPU ve ANE simülasyonu (Gerçek değerler için powermetrics gerekir)
        # VisionAgent aktifken GPU ve ANE yükünü simüle ediyoruz
        gpu_sim = cpu * 0.8 if cpu > 20 else random.uniform(5, 15)
        ane_sim = random.uniform(30, 60) if cpu > 50 else random.uniform(0, 5)

        payload = {
            "agent": "SystemAgent",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "cpu_load": cpu,
                "gpu_load": gpu_sim,
                "ane_load": ane_sim,
                "status": "OPERATIONAL",
            },
        }

        socket.send_json(payload)
        # Terminalde temiz log gör
        print(
            f"[{datetime.now().strftime('%H:%M:%S')}] [SYSTEM] CPU: {cpu}% | GPU: {gpu_sim:.1f}% | ANE: {ane_sim:.1f}%"
        )
        time.sleep(0.5)


if __name__ == "__main__":
    run_system_agent()
