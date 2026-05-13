# SENTINEL_ALPHA/agents/system_agent.py

import psutil
import json
import time
import zmq
from datetime import datetime


class SystemAgent:
    def __init__(self, port=5557):
        # ZeroMQ Setup (PUB)
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

        print(f"[SYSTEM_AGENT] M2 Telemetri Ajanı aktif. Port: {port}")

    def get_system_stats(self):
        # CPU çekirdekleri kullanım yüzdesi
        cpu_usage = psutil.cpu_percent(interval=1, percpu=True)
        # Bellek kullanımı
        memory = psutil.virtual_memory()

        # M2 özelinde GPU verisi standart kütüphanelerle zordur
        # ancak toplam yükü takip etmek referans verir.
        return {
            "cpu_total": sum(cpu_usage) / len(cpu_usage),
            "cpu_cores": cpu_usage,
            "ram_usage": memory.percent,
            "status": "Optimal" if memory.percent < 80 else "Warning",
        }

    def run(self):
        print("[SYSTEM_AGENT] Veri yayını başlatıldı...")
        try:
            while True:
                stats = self.get_system_stats()

                # ZMQ Standart JSON Şeması
                telemetry_data = {
                    "timestamp": datetime.now().isoformat(),
                    "agent": "SystemAgent",
                    "event_type": "Health_Check",
                    "confidence": 1.0,
                    "metadata": {
                        "cpu_load": f"{stats['cpu_total']}%",
                        "ram_usage": f"{stats['ram_usage']}%",
                        "status": stats["status"],
                        "m2_thermal_status": "Normal",  # Mac termal verisi için ek araç gerekebilir
                    },
                }

                # Veriyi PUB portundan fırlat
                self.socket.send_json(telemetry_data)

                # Her 5 saniyede bir güncelle
                time.sleep(5)

        except KeyboardInterrupt:
            print("[SYSTEM_AGENT] Kapatılıyor...")
        finally:
            self.socket.close()
            self.context.term()


if __name__ == "__main__":
    agent = SystemAgent()
    agent.run()
