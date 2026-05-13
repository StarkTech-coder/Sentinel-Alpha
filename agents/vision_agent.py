# SENTINEL_ALPHA/agents/vision_agent.py

import cv2
import json
import time
import zmq
import torch
from ultralytics import YOLO
from datetime import datetime


class VisionAgent:
    def __init__(self, model_path="ai_models/yolov8n.pt", port=5555):
        # ZeroMQ Setup
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

        print(f"[VISION_AGENT] Yerel model yükleniyor: {model_path}")

        # Model Yükleme
        self.model = YOLO(model_path)

        # M2 GPU (Metal) Hızlandırma
        if torch.backends.mps.is_available():
            self.model.to("mps")
            print("[VISION_AGENT] M2 GPU (Metal) Hızlandırma Aktif.")
        else:
            print("[VISION_AGENT] MPS aktif değil, CPU modunda çalışıyor.")

        self.target_labels = {0: "Person", 4: "Airplane", 8: "Boat"}

    def start_capture(self):
        cap = cv2.VideoCapture(0)
        # M2 için performans optimizasyonu
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("[VISION_AGENT] Kamera aktif. Gözlem başlatıldı...")

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                # YOLO Analizi
                results = self.model(frame, stream=True, verbose=False)

                for r in results:
                    for box in r.boxes:
                        cls_id = int(box.cls[0])
                        if cls_id in self.target_labels:
                            conf = float(box.conf[0])
                            coords = box.xyxy[0].tolist()

                            telemetry = {
                                "timestamp": datetime.utcnow().isoformat(),
                                "agent": "VisionAgent",
                                "event_type": "Detection",
                                "confidence": round(conf, 2),
                                "metadata": {
                                    "target_id": f"TGT_{int(time.time())}",
                                    "coordinates": [int(c) for c in coords],
                                    "label": self.target_labels[cls_id],
                                    "status": (
                                        "Target Locked" if conf > 0.7 else "Tracking"
                                    ),
                                },
                            }
                            self.socket.send_json(telemetry)

                time.sleep(0.001)  # CPU döngü koruması
        except KeyboardInterrupt:
            print("[VISION_AGENT] Durduruluyor...")
        finally:
            cap.release()
            self.socket.close()
            self.context.term()


if __name__ == "__main__":
    agent = VisionAgent()
    agent.start_capture()
