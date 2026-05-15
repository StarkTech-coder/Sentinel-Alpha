import zmq
import base64
import json
import numpy as np
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class UIBridge(QThread):
    vision_signal = pyqtSignal(QImage, list)
    health_signal = pyqtSignal(dict)
    metadata_signal = pyqtSignal(dict)
    acoustic_signal = pyqtSignal(float)

    def __init__(self):
        super().__init__()
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://localhost:5558")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.running = True

    def run(self):
        print("[UI_BRIDGE] Sentinel Sinyal Köprüsü Aktif (Port: 5558)")
        poller = zmq.Poller()
        poller.register(self.subscriber, zmq.POLLIN)

        while self.running:
            try:
                socks = dict(poller.poll(100))
                if self.subscriber in socks:
                    message = self.subscriber.recv_json()
                    agent = message.get("agent")

                    if agent == "VisionAgent":
                        self._process_vision(message)
                    elif agent == "SystemAgent":
                        self._process_system(message)
                    elif agent == "AcousticAgent":
                        self._process_acoustic(message)
                    elif agent == "IntelligenceAgent":
                        analysis_text = message.get("analysis", "")
                        self.metadata_signal.emit({"[SENTINEL_INTEL]": analysis_text})
            except Exception as e:
                print(f"[UI_BRIDGE] Hata: {e}")

    def _process_vision(self, message):
        """DÜZELTİLDİ: Görüntü Agent'tan gelen veriyi çözer ve sinyale basar."""
        try:
            frame_data = message.get("frame")  # Agent 'frame' anahtarıyla gönderiyor
            detections = message.get("detections", [])

            if frame_data:
                # Base64'ü doğrudan QImage'e çeviriyoruz (Daha hızlı)
                img_bytes = base64.b64decode(frame_data)
                qt_img = QImage.fromData(img_bytes)

                # Widget'a gönder
                self.vision_signal.emit(qt_img, detections)

                # Sağ panel için bilgi gönder
                self.metadata_signal.emit(
                    {
                        "agent": "VisionAgent",
                        "status": "STREAMING",
                        "objects": len(detections),
                    }
                )
        except Exception as e:
            print(f"[UI_BRIDGE] Vision İşleme Hatası: {e}")

    def _process_system(self, message):
        metadata = message.get("metadata", {})
        metrics = {
            "cpu": float(metadata.get("cpu_load", 0)),
            "gpu": float(metadata.get("gpu_load", 0)),
            "ane": float(metadata.get("ane_load", 0) or metadata.get("ram_usage", 0)),
        }
        self.health_signal.emit(metrics)
        self.metadata_signal.emit(message)

    def _process_acoustic(self, message):
        level = float(
            message.get("level") or message.get("metadata", {}).get("db_level", 0)
        )
        self.acoustic_signal.emit(level)
        self.metadata_signal.emit(message)

    def stop(self):
        self.running = False
        self.wait()
        self.subscriber.close()
        self.context.term()
