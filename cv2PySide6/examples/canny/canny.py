"""Canny edge detection example"""


import cv2
import enum
from numpy.typing import NDArray
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton
from cv2PySide6 import QVideoFrame2Array, NDArrayVideoPlayerWidget


class CannyPipeline(QVideoFrame2Array):

    class CannyMode(enum.Enum):
        Off = 0
        On = 1

    CannyOff = CannyMode.Off
    CannyOn = CannyMode.On

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCannyMode(self.CannyOff)

    def cannyMode(self) -> CannyMode:
        return self._canny_mode

    def setCannyMode(self, mode: CannyMode):
        self._canny_mode = mode

    @Slot(bool)
    def toggleCanny(self, state: bool):
        if state:
            mode = self.CannyOn
        else:
            mode = self.CannyOff
        self.setCannyMode(mode)

    def processArray(self, array: NDArray) -> NDArray:
        rgba = super().processArray(array)
        if self.cannyMode() == self.CannyOn:
            gray = cv2.cvtColor(rgba, cv2.COLOR_RGBA2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGBA)
        elif self.cannyMode() == self.CannyOff:
            ret = rgba
        else:
            raise TypeError("Wrong canny mode : %s" % self.cannyMode())
        return ret


class CannyVideoPlayerWidget(NDArrayVideoPlayerWidget):

    def constructWidgets(self):
        super().constructWidgets()
        self._canny_button = QPushButton("Canny")

    def initWidgets(self):
        self._array_source = CannyPipeline()
        self._video_widget.setArraySource(self._array_source)
        super().initWidgets()
        self._canny_button.setCheckable(True)
        self._canny_button.toggled.connect(self.toggleCanny)

    def initUI(self):
        super().initUI()
        self._main_layout.addWidget(self._canny_button)

    def toggleCanny(self, state: bool):
        self._array_source.toggleCanny(state)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from cv2PySide6 import get_data_path

    app = QApplication(sys.argv)
    player = CannyVideoPlayerWidget()
    geometry = player.screen().availableGeometry()
    player.resize(geometry.width() / 3, geometry.height() / 2)
    player.open(get_data_path("hello.mp4"))
    player.show()
    app.exec()
    app.quit()
