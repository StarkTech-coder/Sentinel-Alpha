import psutil
import zmq
import time
from datetime import datetime


def run_system_agent():
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5557")

    print("[SYSTEM_AGENT] M2 Telemetri Ajanı aktif. Port: 5557")

    while True:
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent

        # --- KRİTİK NOKTA: İSİMLER UI_BRIDGE İLE AYNI OLMALI ---
        payload = {
            "agent": "SystemAgent",
            "timestamp": datetime.now().isoformat(),
            "metadata": {
                "cpu_load": cpu,  # 'cpu' değil 'cpu_load'
                "ram_usage": ram,  # 'ram' değil 'ram_usage'
                "status": "ACTIVE",
            },
        }

        socket.send_json(payload)
        print(f"[{datetime.now().isoformat()}] [SYSTEM] CPU: {cpu}% | RAM: {ram}%")
        time.sleep(0.5)  # Yarım saniyede bir güncelleme yeterli


if __name__ == "__main__":
    run_system_agent()
