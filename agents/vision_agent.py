import cv2
import zmq
import base64
import time
import json
from datetime import datetime
from ultralytics import YOLO


def run_vision_agent():
    # 1. ZMQ KURULUMU (Master Router'a Bağlantı)
    context = zmq.Context()
    # ARTIK PUSH: Veriyi merkeze fırlatıyoruz
    socket = context.socket(zmq.PUSH)
    socket.connect("tcp://localhost:5555")  # Master Router'ın giriş portu

    # 2. YOLOv8 M2 GPU (MPS) YÜKLEME
    try:
        model = YOLO("ai_models/yolov8n.pt")
        model.to("mps")  # Apple Silicon Gücü!
        print("[VISION] YOLOv8n M2 Neural Engine üzerinde aktif.")
    except Exception as e:
        print(f"[ERROR] Model yüklenemedi: {e}")
        return

    cap = cv2.VideoCapture(0)

    # Performans için kamera çözünürlüğünü sabitleyelim
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    print("[VISION] Yayın başlıyor... Çıkmak için CTRL+C")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # 3. NESNE TESPİT (Inference)
        # MPS cihazında koşturuyoruz
        results = model(frame, device="mps", verbose=False)

        detections = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                label = model.names[int(box.cls[0])]

                detections.append(
                    {
                        "label": label,
                        "conf": round(conf, 2),
                        "coordinates": [int(x1), int(y1), int(x2), int(y2)],
                    }
                )

        # 4. GÖRÜNTÜYÜ SIKIŞTIR VE BASE64 YAP
        # JPEG kalitesini 70 yaparak telsiz hattını (ZMQ) yormuyoruz
        _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 70])
        frame_base64 = base64.b64encode(buffer).decode("utf-8")

        # 5. PAYLOAD (UI_BRIDGE VE SANTAL UYUMLU)
        message = {
            "agent": "VisionAgent",
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "frame": frame_base64,
            "detections": detections,
            "status": "TARGET LOCKED" if detections else "SCANNING",
        }

        # Veriyi Santrale Fırlat
        try:
            socket.send_json(message)
        except Exception as e:
            print(f"[VISION_ERROR] Gönderim hatası: {e}")

        # M2 termal dengesi ve CPU kullanımı için minik bir mola
        time.sleep(0.01)

    cap.release()
    socket.close()
    context.term()


if __name__ == "__main__":
    run_vision_agent()
