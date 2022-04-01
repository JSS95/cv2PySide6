"""Video player example with canny edge detection process."""

import cv2 # type: ignore
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Slot, QUrl
from PySide6.QtWidgets import QPushButton
from PySide6.QtMultimedia import QMediaPlayer
from cv2PySide6 import ArrayProcessor, NDArrayVideoPlayerWidget


class CannyEdgeDetector(ArrayProcessor):
    """
    Video pipeline component for Canny edge detection on numpy array.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentArray = np.array((0, 0, 0))
        self._canny_mode = False

    def currentArray(self) -> NDArray:
        """Last array passed to :meth:`setArray`."""
        return self._currentArray

    def cannyMode(self) -> bool:
        """If False, Canny edge detection is not performed."""
        return self._canny_mode

    @Slot(bool)
    def setCannyMode(self, mode: bool):
        self._canny_mode = mode

    @Slot(np.ndarray)
    def setArray(self, array: NDArray):
        self._currentArray = array.copy()
        super().setArray(array)

    def processArray(self, array: NDArray) -> NDArray:
        """Perform Canny edge detection."""
        array = super().processArray(array)
        if self.cannyMode():
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        else:
            ret = array
        return ret

    def refreshCurrentArray(self):
        """Re-process and emit :meth:`currentArray`."""
        self.setArray(self.currentArray())


class CannyVideoPlayerWidget(NDArrayVideoPlayerWidget):

    def __init__(self, parent=None):
        self._cannyButton = QPushButton()
        super().__init__(parent)

        self.setArrayProcessor(CannyEdgeDetector())
        self.cannyButton().setCheckable(True)
        self.cannyButton().toggled.connect(self.onCannyButtonToggle)

    def initUI(self):
        super().initUI()
        self.cannyButton().setText('Toggle edge detection')
        self.layout().addWidget(self.cannyButton())

    def cannyButton(self) -> QPushButton:
        return self._cannyButton

    @Slot(bool)
    def onCannyButtonToggle(self, state: bool):
        self.arrayProcessor().setCannyMode(state) # type: ignore
        if self.videoPlayer().playbackState() != QMediaPlayer.PlayingState:
            self.arrayProcessor().refreshCurrentArray() # type: ignore


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from cv2PySide6 import get_data_path

    app = QApplication(sys.argv)
    widget = CannyVideoPlayerWidget()
    url = QUrl.fromLocalFile(get_data_path("hello.mp4"))
    widget.videoPlayer().setSource(url)
    widget.show()
    app.exec()
    app.quit()
