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

        # Port Bağlantıları
        self.subscriber.connect("tcp://localhost:5555")  # Vision
        self.subscriber.connect("tcp://localhost:5557")  # System
        self.subscriber.connect("tcp://localhost:5558")  # Acoustic
        self.subscriber.connect("tcp://localhost:5559")  # Intelligence (Ollama)

        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.running = True

    def run(self):
        print("[UI_BRIDGE] Sentinel Sinyal Köprüsü Aktif...")
        while self.running:
            try:
                message = self.subscriber.recv_json()
                agent = message.get("agent")

                if agent == "VisionAgent":
                    # Görüntü Çözme
                    frame_data = base64.b64decode(message.get("frame"))
                    np_data = np.frombuffer(frame_data, dtype=np.uint8)
                    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = img.shape

                    qt_img = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)
                    detections = message.get("detections", [])
                    self.vision_signal.emit(qt_img, detections)

                    # Sağ Panel Özeti
                    summary_msg = {
                        "agent": "VisionAgent",
                        "detections_count": len(detections),
                        "status": "STREAMING",
                        "resolution": f"{w}x{h}",
                    }
                    self.metadata_signal.emit(summary_msg)

                elif agent == "SystemAgent":
                    metadata = message.get("metadata", {})
                    metrics = {
                        "cpu": float(metadata.get("cpu_load", 0)),
                        "gpu": float(metadata.get("gpu_load", 0)),
                        "ane": float(metadata.get("ane_load", 0)),
                    }
                    self.health_signal.emit(metrics)
                    self.metadata_signal.emit(message)

                elif agent == "AcousticAgent":
                    level = float(message.get("level", 0))
                    self.acoustic_signal.emit(level)
                    self.metadata_signal.emit(message)

                # Yeni IntelligenceAgent (Ollama) Bloğu - Etiket Güncellendi
                elif agent == "IntelligenceAgent":
                    analysis_text = message.get("analysis", "")
                    self.metadata_signal.emit({"[SENTINEL_INTEL]": analysis_text})

            except Exception as e:
                print(f"[UI_BRIDGE] Veri İşleme Hatası: {e}")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
