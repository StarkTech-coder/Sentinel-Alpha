import zmq
import base64
import json
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class UIBridge(QThread):
    # Widget'lara veri taşıyacak özel sinyaller
    vision_signal = pyqtSignal(QImage, list)  # Görüntü ve Tespit Listesi
    health_signal = pyqtSignal(float, float)  # CPU ve RAM verisi
    metadata_signal = pyqtSignal(dict)  # Tüm ham JSON verisi

    def __init__(self):
        super().__init__()
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)

        # Tüm ajan portlarını dinle
        self.subscriber.connect("tcp://localhost:5555")  # Vision
        self.subscriber.connect("tcp://localhost:5557")  # System
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")

        self.running = True

    def run(self):
        print("[UI_BRIDGE] Sinyal köprüsü kuruldu. Veri akışı bekleniyor...")
        while self.running:
            try:
                # Mesajı al
                message = self.subscriber.recv_json()
                agent = message.get("agent")

                if agent == "VisionAgent":
                    # 1. Görüntüyü Çöz (Base64 -> QImage)
                    frame_data = base64.b64decode(message.get("frame"))
                    np_data = np.frombuffer(frame_data, dtype=np.uint8)

                    # Görüntü işleme (OpenCV formatından QImage formatına)
                    import cv2

                    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                    h, w, ch = img.shape
                    bytes_per_line = ch * w
                    qt_img = QImage(
                        img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888
                    )

                    # Detections listesini al
                    detections = message.get("detections", [])

                    # Arayüze fırlat
                    self.vision_signal.emit(qt_img, detections)

                elif agent == "SystemAgent":
                    metadata = message.get("metadata", {})
                    cpu = float(metadata.get("cpu_load", 0))
                    ram = float(metadata.get("ram_usage", 0))

                    self.health_signal.emit(cpu, ram)

                # Her halükarda metadata paneline veriyi gönder
                self.metadata_signal.emit(message)

            except Exception as e:
                print(f"[UI_BRIDGE] Hata: {e}")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
