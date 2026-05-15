import zmq
import json


class MasterRouter:
    def __init__(self, input_port=5555, output_port=5558):
        self.context = zmq.Context()

        # 1. AJANLARDAN VERİ ALAN KAPI (PULL)
        # Bütün ajanlar (Vision, System, Heat) buraya PUSH yapacak.
        self.receiver = self.context.socket(zmq.PULL)
        self.receiver.bind(f"tcp://*:{input_port}")

        # 2. UI VE DİĞERLERİNE VERİ DAĞITAN KAPI (PUB)
        # Widgetlar buraya SUB (abone) olacak.
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind(f"tcp://*:{output_port}")

        print(f"[MASTER] Santral aktif. Giriş:{input_port} -> Çıkış:{output_port}")

    def start(self):
        try:
            while True:
                # Veriyi ajanlardan al (Hiç içine bakmadan, ham paket olarak)
                message = self.receiver.recv_json()

                # Veriyi olduğu gibi sisteme yay (Forward)
                # Böylece VisionWidget da, HeatWidget da aynı anda duyabilir
                self.publisher.send_json(message)

                # Sadece loglamak için (İstersen kapatabilirsin)
                agent = message.get("agent", "Unknown")
                print(f"[FORWARDING] {agent} verisi dağıtıldı.")

        except KeyboardInterrupt:
            print("[MASTER] Santral kapatılıyor...")
        finally:
            self.receiver.close()
            self.publisher.close()
            self.context.term()


if __name__ == "__main__":
    router = MasterRouter()
    router.start()
