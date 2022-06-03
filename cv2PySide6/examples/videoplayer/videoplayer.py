"""Video player example with multithreaded canny edge detection process."""

import cv2  # type: ignore[import]
from cv2PySide6 import FrameToArrayConverter, MediaController, NDArrayLabel
import numpy as np
import numpy.typing as npt
from PySide6.QtCore import QObject, Signal, Slot, Qt, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout


class CannyEdgeDetector(QObject):
    """
    Video pipeline component for Canny edge detection on numpy array.
    """

    arrayChanged = Signal(np.ndarray)

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

    def setArray(self, array: npt.NDArray[np.uint8]):
        self._currentArray = array

        if array.size > 0 and self.cannyMode():
            gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
            canny = cv2.Canny(gray, 50, 200)
            ret = cv2.cvtColor(canny, cv2.COLOR_GRAY2RGB)
        else:
            ret = array
        self.arrayChanged.emit(ret)

    def refreshCurrentArray(self):
        """Re-process and emit :meth:`currentArray`."""
        self.setArray(self.currentArray())


class CannyVideoPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = QMediaPlayer(self)
        self._frame2Arr = FrameToArrayConverter()
        self._arrayProcessor = CannyEdgeDetector()
        self._videoLabel = NDArrayLabel()
        self._mediaController = MediaController()
        self._cannyButton = QPushButton()

        self.videoPlayer().setVideoSink(QVideoSink(self))
        self.videoPlayer().videoSink().videoFrameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        self.frameToArrayConverter().arrayChanged.connect(
            self.arrayProcessor().setArray
        )
        self.arrayProcessor().arrayChanged.connect(self.videoLabel().setArray)
        self.videoLabel().setAlignment(Qt.AlignCenter)
        self.mediaController().setPlayer(self.videoPlayer())
        self.cannyButton().setCheckable(True)
        self.cannyButton().toggled.connect(self.onCannyButtonToggle)

        self.cannyButton().setText("Toggle edge detection")

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        layout.addWidget(self.mediaController())
        layout.addWidget(self.cannyButton())
        self.setLayout(layout)

    def videoPlayer(self) -> QMediaPlayer:
        return self._videoPlayer

    def frameToArrayConverter(self) -> FrameToArrayConverter:
        return self._frame2Arr

    def arrayProcessor(self) -> CannyEdgeDetector:
        return self._arrayProcessor

    def videoLabel(self) -> NDArrayLabel:
        return self._videoLabel

    def mediaController(self) -> MediaController:
        return self._mediaController

    def cannyButton(self) -> QPushButton:
        return self._cannyButton

    @Slot(bool)
    def onCannyButtonToggle(self, state: bool):
        self.arrayProcessor().setCannyMode(state)
        if self.videoPlayer().playbackState() != self.videoPlayer().PlayingState:
            self.arrayProcessor().refreshCurrentArray()


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
