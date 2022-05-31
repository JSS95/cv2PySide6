"""Video player example with canny edge detection process."""

import cv2  # type: ignore[import]
from cv2PySide6 import ArrayProcessor, NDArrayVideoPlayer, NDArrayLabel, MediaController
import numpy as np
import numpy.typing as npt
from PySide6.QtCore import Slot, Qt, QUrl
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout
from PySide6.QtMultimedia import QMediaPlayer


class CannyEdgeDetector(ArrayProcessor):
    """
    Video pipeline component for Canny edge detection on numpy array.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._currentArray = np.empty((0, 0, 0))
        self._canny_mode = False

    def currentArray(self) -> npt.NDArray[np.uint8]:
        """Last array passed to :meth:`setArray`."""
        return self._currentArray

    def cannyMode(self) -> bool:
        """If False, Canny edge detection is not performed."""
        return self._canny_mode

    @Slot(bool)
    def setCannyMode(self, mode: bool):
        self._canny_mode = mode

    @Slot(np.ndarray)
    def setArray(self, array: npt.NDArray[np.uint8]):
        self._currentArray = array.copy()
        super().setArray(array)

    def processArray(self, array: npt.NDArray[np.uint8]) -> npt.NDArray[np.uint8]:
        """Perform Canny edge detection."""
        array = super().processArray(array)
        if array.size > 0 and self.cannyMode():
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        else:
            ret = array
        return ret

    def refreshCurrentArray(self):
        """Re-process and emit :meth:`currentArray`."""
        self.setArray(self.currentArray())


class CannyVideoPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._arrayProcessor = CannyEdgeDetector()
        self._videoLabel = NDArrayLabel()
        self._videoController = MediaController()
        self._cannyButton = QPushButton()

        self.videoPlayer().arrayChanged.connect(self.arrayProcessor().setArray)
        self.arrayProcessor().arrayChanged.connect(self.videoLabel().setArray)
        self.videoLabel().setAlignment(Qt.AlignCenter)
        self.videoController().setPlayer(self.videoPlayer())
        self.cannyButton().setCheckable(True)
        self.cannyButton().toggled.connect(self.onCannyButtonToggle)

        self.cannyButton().setText("Toggle edge detection")

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        layout.addWidget(self.videoController())
        layout.addWidget(self.cannyButton())
        self.setLayout(layout)

    def videoPlayer(self) -> NDArrayVideoPlayer:
        return self._videoPlayer

    def arrayProcessor(self) -> CannyEdgeDetector:
        return self._arrayProcessor

    def videoLabel(self) -> NDArrayLabel:
        return self._videoLabel

    def videoController(self) -> MediaController:
        return self._videoController

    def cannyButton(self) -> QPushButton:
        return self._cannyButton

    @Slot(bool)
    def onCannyButtonToggle(self, state: bool):
        self.arrayProcessor().setCannyMode(state)
        if self.videoPlayer().playbackState() != QMediaPlayer.PlayingState:
            self.arrayProcessor().refreshCurrentArray()

    def closeEvent(self, event: QCloseEvent):
        self.videoPlayer().stop()
        event.accept()


if __name__ == "__main__":
    from cv2PySide6 import get_data_path
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = CannyVideoPlayerWidget()
    url = QUrl.fromLocalFile(get_data_path("hello.mp4"))
    widget.videoPlayer().setSource(url)
    widget.show()
    app.exec()
    app.quit()
