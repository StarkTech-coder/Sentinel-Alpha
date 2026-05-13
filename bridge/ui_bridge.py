import zmq
import base64
import json
import numpy as np
import cv2
from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QImage


class UIBridge(QThread):
    vision_signal = pyqtSignal(QImage, list)
    health_signal = pyqtSignal(float, float)
    metadata_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.context = zmq.Context()
        self.subscriber = self.context.socket(zmq.SUB)
        self.subscriber.connect("tcp://localhost:5555")
        self.subscriber.connect("tcp://localhost:5557")
        self.subscriber.setsockopt_string(zmq.SUBSCRIBE, "")
        self.running = True

    def run(self):
        print("[UI_BRIDGE] Sinyal köprüsü kuruldu. Veri akışı bekleniyor...")
        while self.running:
            try:
                message = self.subscriber.recv_json()
                agent = message.get("agent")

                # Metadata paneli için mesajın bir kopyasını al ve temizle
                display_msg = message.copy()

                if agent == "VisionAgent":
                    # Görüntüyü işle
                    frame_data = base64.b64decode(message.get("frame"))
                    np_data = np.frombuffer(frame_data, dtype=np.uint8)
                    img = cv2.imdecode(np_data, cv2.IMREAD_COLOR)
                    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    h, w, ch = img.shape
                    qt_img = QImage(img.data, w, h, ch * w, QImage.Format.Format_RGB888)

                    detections = message.get("detections", [])
                    self.vision_signal.emit(qt_img, detections)

                    # Sağ üst panelde o Base64 yığınını görmemek için 'frame'i siliyoruz
                    if "frame" in display_msg:
                        display_msg["frame"] = "[IMAGE_DATA_OMITTED]"

                elif agent == "SystemAgent":
                    metadata = message.get("metadata", {})
                    # Agent'tan gelen verinin anahtarlarıyla (cpu_load/ram_usage) eşleştiğine emin ol
                    cpu = float(metadata.get("cpu_load", 0))
                    ram = float(metadata.get("ram_usage", 0))

                    print(
                        f"[UI_BRIDGE] System Data Received: CPU {cpu} RAM {ram}"
                    )  # Terminalden kontrol için
                    self.health_signal.emit(cpu, ram)

                # Temizlenmiş veriyi sağ üstteki Metadata paneline gönder
                self.metadata_signal.emit(display_msg)

            except Exception as e:
                print(f"[UI_BRIDGE] Hata: {e}")

    def stop(self):
        self.running = False
        self.quit()
        self.wait()
