from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen, QColor, QFont


class VisionWidget(QLabel):
    def __init__(self):
        super().__init__()
        # Başlangıç metni ve stili
        self.setText("SENTINEL VISION FEED\n[WAITING FOR STREAM]")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)

        # Dashboard temasına uygun Sentinel Yeşili stili
        self.setStyleSheet("""
            border: 2px solid #00FF41; 
            background-color: #000; 
            font-family: 'Courier New'; 
            color: #00FF41;
            font-weight: bold;
            """)

        self.latest_detections = []
        self.original_image_size = (640, 480)

    def update_frame(self, qt_img, detections):
        """Bridge üzerinden gelen görüntüyü ve YOLO tespitlerini işler."""
        self.latest_detections = detections
        self.original_image_size = (qt_img.width(), qt_img.height())

        # Görüntüyü widget boyutuna ölçekle
        pixmap = QPixmap.fromImage(qt_img).scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.setPixmap(pixmap)

        # paintEvent'i tetikleyerek çizimleri günceller
        self.update()

    def paintEvent(self, event):
        """Görüntü üzerine HUD braketlerini ve YOLO köşe işaretlerini çizer."""
        super().paintEvent(event)

        if not self.pixmap():
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Sentinel Yeşili Ayarları
        sentinel_green = QColor(0, 255, 65)
        painter.setPen(QPen(sentinel_green, 2))
        painter.setFont(QFont("Courier New", 9, QFont.Weight.Bold))

        # 1. ANA HUD KÖŞE BRAKETLERİ (Sabit Vizör)
        w, h = self.width(), self.height()
        m, l = 20, 40  # Margin ve Length

        # Vizör köşeleri
        painter.drawLine(m, m, m + l, m)
        painter.drawLine(m, m, m, m + l)  # Sol Üst
        painter.drawLine(w - m, m, w - m - l, m)
        painter.drawLine(w - m, m, w - m, m + l)  # Sağ Üst
        painter.drawLine(m, h - m, m + l, h - m)
        painter.drawLine(m, h - m, m, h - m - l)  # Sol Alt
        painter.drawLine(w - m, h - m, w - m - l, h - m)
        painter.drawLine(w - m, h - m, w - m, h - m - l)  # Sağ Alt

        # 2. YOLO TESPİT KÖŞE BRAKETLERİ
        if self.latest_detections:
            # Görüntü ölçeklendiği için koordinatları oranlıyoruz
            scale_x = self.width() / self.original_image_size[0]
            scale_y = self.height() / self.original_image_size[1]

            for det in self.latest_detections:
                coords = det.get("coordinates", [0, 0, 0, 0])
                label = det.get("label", "Unknown").upper()
                conf = det.get("conf", 0.0)

                # Oranlanmış koordinatlar
                x1 = int(coords[0] * scale_x)
                y1 = int(coords[1] * scale_y)
                x2 = int(coords[2] * scale_x)
                y2 = int(coords[3] * scale_y)

                # Dinamik braket uzunluğu
                b_len = 15

                # Nesne Köşe Çizimleri
                # Sol Üst
                painter.drawLine(x1, y1, x1 + b_len, y1)
                painter.drawLine(x1, y1, x1, y1 + b_len)
                # Sağ Üst
                painter.drawLine(x2, y1, x2 - b_len, y1)
                painter.drawLine(x2, y1, x2, y1 + b_len)
                # Sol Alt
                painter.drawLine(x1, y2, x1 + b_len, y2)
                painter.drawLine(x1, y2, x1, y2 - b_len)
                # Sağ Alt
                painter.drawLine(x2, y2, x2 - b_len, y2)
                painter.drawLine(x2, y2, x2, y2 - b_len)

                # Minimalist Etiket (Sadece Sol Üst Köşeye)
                painter.drawText(x1 + 5, y1 - 5, f"> {label} {int(conf*100)}%")

        painter.end()
