import cv2
import json
import time
import zmq
import base64
import numpy as np
from ultralytics import YOLO
from datetime import datetime


class VisionAgent:
    def __init__(self, model_path="ai_models/yolov8n.mlpackage", port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")

        print(f"[VISION_AGENT] ANE Modeli Yükleniyor: {model_path}")
        self.model = YOLO(model_path, task="detect")

        # CoreML'de model.names bazen geç yüklenir. Eğer None ise boş bir sözlük ata.
        self.names = self.model.names if self.model.names else {}
        self.hud_color = (0, 255, 0)

    def draw_hud_corners(self, img, box, color=(0, 255, 0), thickness=2, length=20):
        x1, y1, x2, y2 = map(int, box)
        cv2.line(img, (x1, y1), (x1 + length, y1), color, thickness)
        cv2.line(img, (x1, y1), (x1, y1 + length), color, thickness)
        cv2.line(img, (x2, y1), (x2 - length, y1), color, thickness)
        cv2.line(img, (x2, y1), (x2, y1 + length), color, thickness)
        cv2.line(img, (x1, y2), (x1 + length, y2), color, thickness)
        cv2.line(img, (x1, y2), (x1, y2 - length), color, thickness)
        cv2.line(img, (x2, y2), (x2 - length, y2), color, thickness)
        cv2.line(img, (x2, y2), (x2, y2 - length), color, thickness)

    def start_capture(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        try:
            while cap.isOpened():
                success, frame = cap.read()
                if not success:
                    break

                results = self.model(frame, stream=True, verbose=False, device="mps")

                detections = []

                for r in results:
                    # Model isimleri hala None ise buradan tekrar kontrol et (CoreML için kritik)
                    if not self.names and r.names:
                        self.names = r.names

                    if r.boxes:
                        for box in r.boxes:
                            conf = float(box.conf[0])
                            if conf < 0.3:
                                continue

                            cls_id = int(box.cls[0])
                            # Hata kontrolü: Eğer isim hala yoksa ID'yi kullan
                            label = self.names.get(cls_id, f"obj_{cls_id}")

                            coords = box.xyxy[0].tolist()

                            self.draw_hud_corners(frame, coords, color=self.hud_color)
                            cv2.putText(
                                frame,
                                f"{label.upper()} {conf:.2f}",
                                (int(coords[0]), int(coords[1]) - 10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.4,
                                self.hud_color,
                                1,
                            )

                            detections.append({"label": label, "conf": round(conf, 2)})

                _, buffer = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                jpg_as_text = base64.b64encode(buffer).decode("utf-8")

                telemetry = {
                    "timestamp": datetime.now().isoformat(),
                    "agent": "VisionAgent",
                    "frame": jpg_as_text,
                    "detections": detections,
                    "metadata": {"status": "ACTIVE SCANNING" if detections else "IDLE"},
                }
                self.socket.send_json(telemetry)
                time.sleep(0.04)

        except Exception as e:
            print(f"[VISION_AGENT] Çevrim içi hata: {e}")
        finally:
            cap.release()
            self.socket.close()


if __name__ == "__main__":
    agent = VisionAgent()
    agent.start_capture()
