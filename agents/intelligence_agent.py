import zmq
import json
import requests
import time
from datetime import datetime


class IntelligenceAgent:
    def __init__(self):
        self.context = zmq.Context()
        # Veri toplamak için SUB soketi
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://localhost:5555")  # Vision
        self.subscriber.connect("tcp://localhost:5557")  # System
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # Sonuçları Dashboard'a basmak için PUB soketi
        self.publisher = self.context.socket(zmq.PUB)
        self.publisher.bind("tcp://*:5559")

        self.ollama_url = "http://localhost:11434/api/generate"
        self.current_data = {"vision": [], "system": {}}

    def get_ollama_analysis(self, prompt):
        try:
            payload = {
                "model": "llama3.1",  # M2'de en iyi bu çalışır
                "prompt": prompt,
                "stream": False,
            }
            response = requests.post(self.ollama_url, json=payload)
            return response.json().get("response", "Analiz başarısız.")
        except:
            return "Ollama bağlantısı kurulamadı."

    def run(self):
        print("[INTEL] Intelligence Agent aktif. Ollama dinleniyor...")
        last_analysis_time = time.time()

        while True:
            try:
                # Verileri topla
                msg = self.subscriber.recv_json(flags=zmq.NOBLOCK)
                if msg["agent"] == "VisionAgent":
                    self.current_data["vision"] = msg.get("detections", [])
                elif msg["agent"] == "SystemAgent":
                    self.current_data["system"] = msg.get("metadata", {})
            except zmq.Again:
                pass

            # Her 10 saniyede bir yorum yap (M2'yi yormamak için)
            if time.time() - last_analysis_time > 10:
                prompt = f"""
                Sen SENTINEL AI sisteminin beynisin. Şu anki verileri analiz et:
                Görülen Nesneler: {self.current_data['vision']}
                Sistem Durumu: CPU %{self.current_data['system'].get('cpu_load')}, RAM %{self.current_data['system'].get('ram_usage')}
                Kısa, askeri tarzda bir rapor ver.
                """
                analysis = self.get_ollama_analysis(prompt)

                # Sonucu UI'ya yolla
                self.publisher.send_json(
                    {
                        "agent": "IntelligenceAgent",
                        "analysis": analysis,
                        "timestamp": datetime.now().isoformat(),
                    }
                )
                last_analysis_time = time.time()

            time.sleep(0.1)


if __name__ == "__main__":
    IntelligenceAgent().run()
