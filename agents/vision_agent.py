# SENTINEL_ALPHA/agents/vision_agent.py

import cv2
import json
import time
import zmq
from ultralytics import YOLO
from datetime import datetime


class VisionAgent:
    def __init__(self, model_path="ai_models/yolov8n.mlpackage", port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

        print(f"[VISION_AGENT] ANE Modeli Yükleniyor: {model_path}")

        # Task'ı açıkça belirterek o uyarıyı da siliyoruz
        self.model = YOLO(model_path, task="detect")

        # Hedef Etiketleri
        self.target_labels = {0: "Person", 4: "Airplane", 8: "Boat"}

    def start_capture(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        print("[VISION_AGENT] Gözlem ANE üzerinden aktif edildi.")

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                # Inference
                results = self.model(frame, stream=True, verbose=False)

                for r in results:
                    # Ultralytics burada NMS'i kendi yapacak
                    if r.boxes:
                        for box in r.boxes:
                            cls_id = int(box.cls[0])
                            if cls_id in self.target_labels:
                                conf = float(box.conf[0])
                                coords = box.xyxy[0].tolist()

                                telemetry = {
                                    "timestamp": datetime.now().isoformat(),
                                    "agent": "VisionAgent",
                                    "event_type": "Detection",
                                    "confidence": round(conf, 2),
                                    "metadata": {
                                        "target_id": f"TGT_{int(time.time())}",
                                        "coordinates": [int(c) for c in coords],
                                        "label": self.target_labels[cls_id],
                                        "status": (
                                            "Target Locked"
                                            if conf > 0.7
                                            else "Tracking"
                                        ),
                                    },
                                }
                                self.socket.send_json(telemetry)

                time.sleep(0.001)
        except Exception as e:
            print(f"[VISION_AGENT] Kritik Hata: {e}")
        finally:
            cap.release()
            self.socket.close()
            self.context.term()


if __name__ == "__main__":
    agent = VisionAgent()
    agent.start_capture()
