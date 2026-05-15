import zmq
import json
import requests
import time
import os
from datetime import datetime


class IntelligenceAgent:
    def __init__(self):
        self.context = zmq.Context()

        # 1. VERİ ALMA: Santralin ÇIKIŞ portundan (5558) abone oluyoruz
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://localhost:5558")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        # 2. ANALİZ VE REFLEKS GÖNDERME: Santralin GİRİŞ portuna (5555) PUSH yapıyoruz
        self.publisher = self.context.socket(zmq.PUSH)
        self.publisher.connect("tcp://localhost:5555")

        self.ollama_url = "http://localhost:11434/api/generate"
        self.memory = {"vision": [], "system": {}, "last_analysis": ""}

    def execute_instant_reflex(self, detections):
        """
        KATMAN 1: OLLAMA ÖNCESİ HIZLI REFLEKS
        Bu fonksiyon saliseler içinde çalışır.
        """
        critical_targets = [
            "weapon",
            "fire",
            "knife",
            "intruder",
            "person",
        ]  # Test için 'person' ekledim

        for det in detections:
            label = det.get("label", "").lower()
            if label in critical_targets:
                # ANLIK REFLEKS PAKETİ (Ollama'yı beklemeden fırlatıyoruz)
                reflex_msg = {
                    "agent": "IntelligenceAgent",
                    "type": "REFLEX",
                    "reflex_level": "CRITICAL",
                    "target": label.upper(),
                    "timestamp": datetime.now().strftime("%H:%M:%S.%f")[:-3],
                }
                self.publisher.send_json(reflex_msg)
                print(f"[REFLEX] KRİTİK HEDEF TESPİT EDİLDİ: {label.upper()}!")

                # İsteğe bağlı: Mac'e sesli uyarı verdir
                # os.system(f'say "Alert! {label} detected." &')
                return True
        return False

    def get_ollama_analysis(self, prompt):
        """KATMAN 2: STRATEJİK ANALİZ (DERİN DÜŞÜNCE)"""
        try:
            payload = {
                "model": "llama3.1",
                "prompt": f"Sen bir savunma sanayii yapay zekasısın. Vereceğim verileri askeri tonda analiz et. Yanıtın kısa olsun. Veriler: {prompt}",
                "stream": False,
            }
            response = requests.post(self.ollama_url, json=payload, timeout=10)
            return response.json().get("response", "Analiz verisi alınamadı.")
        except Exception as e:
            return f"Ollama hatası: {str(e)}"

    def run(self):
        print(
            "[INTEL] Intelligence Agent (Refleks + Ollama) Aktif. Santral Dinleniyor..."
        )
        last_report_time = time.time()

        while True:
            try:
                # Santralden gelen her şeyi dinle
                while True:
                    try:
                        msg = self.subscriber.recv_json(flags=zmq.NOBLOCK)
                        agent = msg.get("agent")

                        if agent == "VisionAgent":
                            detections = msg.get("detections", [])
                            self.memory["vision"] = detections

                            # --- ⚡ REFLEKS KONTROLÜ (HER KAREDE) ---
                            # Ollama'nın 15 saniyelik periyodunu beklemez!
                            self.execute_instant_reflex(detections)

                        elif agent == "SystemAgent":
                            self.memory["system"] = msg.get("metadata", {})

                    except zmq.Again:
                        break

                # --- 🐢 STRATEJİK ANALİZ (15 SANIYEDE BIR) ---
                if time.time() - last_report_time > 15:
                    print("[INTEL] Stratejik rapor hazırlanıyor...")

                    report_prompt = (
                        f"Görülenler: {self.memory['vision']} | "
                        f"Sistem Durumu: CPU %{self.memory['system'].get('cpu_load', 0)}"
                    )

                    analysis = self.get_ollama_analysis(report_prompt)

                    self.publisher.send_json(
                        {
                            "agent": "IntelligenceAgent",
                            "type": "STRATEGIC_REPORT",
                            "analysis": analysis,
                            "timestamp": datetime.now().strftime("%H:%M:%S"),
                        }
                    )

                    last_report_time = time.time()

            except Exception as e:
                print(f"[INTEL_ERROR] {e}")

            time.sleep(0.01)  # Hız için sleep süresini düşürdük


if __name__ == "__main__":
    IntelligenceAgent().run()
