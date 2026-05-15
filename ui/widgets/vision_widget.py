import sys
import json
import base64
import numpy as np
import cv2
from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont


class VisionWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("SENTINEL VISION FEED\n[WAITING FOR DATA...]")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)

        # Siber Stil
        self.setStyleSheet("""
            border: 2px solid #00FF41; 
            background-color: #000; 
            font-family: 'Courier New'; 
            color: #00FF41;
            font-weight: bold;
        """)

        self.latest_detections = []
        self.current_frame = None

    def update_frame(self, qt_img, detections):
        """UIBridge'den gelen hazır QImage ve tespitleri alır."""
        try:
            self.current_frame = qt_img
            self.latest_detections = detections

            # Görüntüyü ekrana sığdır ve bas
            pixmap = QPixmap.fromImage(self.current_frame).scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.setPixmap(pixmap)

            # Braketlerin çizilmesi için paintEvent'i tetikle
            self.update()
        except Exception as e:
            print(f"[VISION_WIDGET_ERROR] Update hatası: {e}")

    def paintEvent(self, event):
        """Görüntü üzerine HUD braketlerini ve YOLO kutularını çizer."""
        super().paintEvent(event)

        # Eğer görüntü yoksa çizim yapma
        if not self.current_frame or self.pixmap() is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Sentinel Yeşili
        green = QColor(0, 255, 65)
        painter.setPen(QPen(green, 2))
        painter.setFont(QFont("Courier New", 10, QFont.Weight.Bold))

        # 1. SABİT HUD KÖŞELERİ (Görsel efekt)
        w, h = self.width(), self.height()
        m, l = 20, 40  # Kenar boşluğu ve çizgi boyu

        # Sol Üst
        painter.drawLine(m, m, m + l, m)
        painter.drawLine(m, m, m, m + l)
        # Sağ Üst
        painter.drawLine(w - m, m, w - m - l, m)
        painter.drawLine(w - m, m, w - m, m + l)
        # Sol Alt
        painter.drawLine(m, h - m, m + l, h - m)
        painter.drawLine(m, h - m, m, h - m - l)
        # Sağ Alt
        painter.drawLine(w - m, h - m, w - m - l, h - m)
        painter.drawLine(w - m, h - m, w - m, h - m - l)

        # 2. YOLO TESPİT BRAKETLERİ
        if self.latest_detections:
            # Görüntü ölçekleme (Pencere boyutu değiştikçe kutular kaymasın diye)
            scale_x = self.width() / self.current_frame.width()
            scale_y = self.height() / self.current_frame.height()

            for det in self.latest_detections:
                coords = det.get("coordinates", [0, 0, 0, 0])
                label = det.get("label", "TARGET").upper()
                conf = det.get("conf", 0.0)

                # Koordinatları pencereye uyarla
                x1, y1 = int(coords[0] * scale_x), int(coords[1] * scale_y)
                x2, y2 = int(coords[2] * scale_x), int(coords[3] * scale_y)

                b = 15  # Köşe braket boyu

                # Nesne etrafına dinamik braketler
                # Üst köşeler
                painter.drawLine(x1, y1, x1 + b, y1)
                painter.drawLine(x1, y1, x1, y1 + b)
                painter.drawLine(x2, y1, x2 - b, y1)
                painter.drawLine(x2, y1, x2, y1 + b)
                # Alt köşeler
                painter.drawLine(x1, y2, x1 + b, y2)
                painter.drawLine(x1, y2, x1, y2 - b)
                painter.drawLine(x2, y2, x2 - b, y2)
                painter.drawLine(x2, y2, x2, y2 - b)

                # Bilgi metni
                painter.drawText(x1 + 5, y1 - 5, f">> {label} {int(conf*100)}%")

        painter.end()
