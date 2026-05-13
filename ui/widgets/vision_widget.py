from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QImage, QPixmap


class VisionWidget(QLabel):
    def __init__(self):
        super().__init__()
        self.setText("SENTINEL VISION FEED\n[WAITING FOR STREAM]")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setMinimumSize(640, 480)
        self.setStyleSheet(
            "border: 2px solid #00f2ff; background-color: #000; font-family: 'Courier New'; color: #00f2ff;"
        )

    def update_frame(self, qt_img):
        self.setPixmap(
            QPixmap.fromImage(qt_img).scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )
