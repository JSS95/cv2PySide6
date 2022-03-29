"""Canny edge detection example"""


import cv2 # type: ignore
import enum
from numpy.typing import NDArray
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QPushButton
from PySide6.QtMultimedia import QMediaPlayer
from cv2PySide6 import FrameToArrayConverter, NDArrayVideoPlayerWidget


class CannyEdgeDetector(FrameToArrayConverter):

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
        array = super().processArray(array)
        if self.cannyMode() == self.CannyOn:
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        elif self.cannyMode() == self.CannyOff:
            ret = array
        else:
            raise TypeError("Wrong canny mode : %s" % self.cannyMode())
        return ret

    def resetArray(self):
        self.arrayChanged.emit(self.processArray(self.array()))


class CannyVideoPlayerWidget(NDArrayVideoPlayerWidget):

    def constructWidgets(self):
        super().constructWidgets()
        self._canny_button = QPushButton("Canny")

    def initWidgets(self):
        self._array_source = CannyEdgeDetector()
        self._video_widget.setArraySource(self._array_source)
        super().initWidgets()
        self._canny_button.setCheckable(True)
        self._canny_button.toggled.connect(self.toggleCanny)

    def initUI(self):
        super().initUI()
        self._main_layout.addWidget(self._canny_button)

    def toggleCanny(self, state: bool):
        self._array_source.toggleCanny(state)
        if self._player.playbackState() != QMediaPlayer.PlayingState:
            self._array_source.resetArray()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from cv2PySide6 import get_data_path

    app = QApplication(sys.argv)
    player = CannyVideoPlayerWidget()
    player.open(get_data_path("hello.mp4"))
    player.show()
    app.exec()
    app.quit()
