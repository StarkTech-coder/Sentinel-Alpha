import zmq
import json


class MasterRouter:
    def __init__(self, vision_port=5555, system_port=5557):
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)

        # Ajan bağlantıları
        self.subscriber.connect(f"tcp://localhost:{vision_port}")
        self.subscriber.connect(f"tcp://localhost:{system_port}")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        self.poller = zmq.Poller()
        self.poller.register(self.subscriber, zmq.POLLIN)

        print("[MASTER_ROUTER] Merkezi sinir sistemi aktif. Ajanlar dinleniyor...")

    def listen(self):
        try:
            while True:
                socks = dict(self.poller.poll(1000))
                if self.subscriber in socks:
                    message = self.subscriber.recv_json()

                    agent_name = message.get("agent")
                    timestamp = message.get("timestamp", "N/A")
                    metadata = message.get("metadata", {})

                    if agent_name == "VisionAgent":
                        # Listeden güvenli çekim
                        detections = message.get("detections", [])
                        if detections:
                            for det in detections:
                                label = det.get("label", "Unknown")
                                conf = det.get("conf", 0.0)
                                print(
                                    f"[{timestamp}] [VISION] Tespit: {label} (%{conf*100})"
                                )
                        else:
                            # Nesne yoksa durum bildir
                            print(
                                f"[{timestamp}] [VISION] Tarama aktif: {metadata.get('status', 'IDLE')}"
                            )

                    elif agent_name == "SystemAgent":
                        # metadata içindeki yeni şemaya göre çekim (SystemAgent koduna göre)
                        cpu = metadata.get("cpu_load", "0.0")
                        ram = metadata.get("ram_usage", "0.0")
                        print(f"[{timestamp}] [SYSTEM] CPU: {cpu}% | RAM: {ram}%")

        except KeyboardInterrupt:
            print("[MASTER_ROUTER] Kesme algılandı...")
        finally:
            self.subscriber.close()
            self.context.term()


if __name__ == "__main__":
    router = MasterRouter()
    router.listen()
