import cv2
import zmq
import base64
import time
import json
from datetime import datetime
from ultralytics import YOLO


def run_vision_agent():
    # 1. ZMQ Kurulumu
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind("tcp://*:5555")

    # 2. YOLOv8 Model Yükleme (M2 GPU/MPS Hızlandırması)
    try:
        model = YOLO("ai_models/yolov8n.pt")
        # MacBook Air M2'nin gücünü (MPS) kullanıyoruz
        model.to("mps")
        print("[VISION] YOLOv8n M2 Neural Engine üzerinde aktif.")
    except Exception as e:
        print(f"[ERROR] Model yüklenemedi: {e}")
        return

    # Mac için alternatif kamera indeksi (Gerekirse 0'ı 1 yap)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 3. Nesne Tespit (M2 MPS üzerinde inference)
        results = model(frame, device="mps", verbose=False)
        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                cls = int(box.cls[0])
                label = model.names[cls]

                detections.append(
                    {
                        "label": label,
                        "conf": round(conf, 2),
                        "coordinates": [int(x1), int(y1), int(x2), int(y2)],
                    }
                )

        # 4. Görüntü İşleme (Base64)
        # Boyutu biraz küçülterek (640x480 gibi) iletimi hızlandırabilirsin
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        frame_base64 = base64.b64encode(buffer).decode("utf-8")

        # 5. UI_BRIDGE İLE TAM UYUMLU PAYLOAD
        # DÜZELTME: 'telemetry' yerine anahtarları dışarı çıkardık
        message = {
            "agent": "VisionAgent",
            "timestamp": datetime.now().isoformat(),
            "frame": frame_base64,
            "detections": detections,  # UIBridge direkt bunu arıyor
            "status": "TARGET LOCKED" if detections else "SCANNING",
        }

        # JSON olarak fırlat
        socket.send_json(message)

        # M2 termal kısıtlamalarını korumak için küçük bir es
        time.sleep(0.01)

    cap.release()


if __name__ == "__main__":
    run_vision_agent()
