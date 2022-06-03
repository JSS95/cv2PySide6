"""Camera example with Gaussian blurring process."""

import cv2  # type: ignore
from cv2PySide6 import NDArrayMediaCaptureSession, NDArrayLabel
import numpy as np
import numpy.typing as npt
from PySide6.QtCore import QObject, Signal, Slot, Qt
from PySide6.QtWidgets import QMainWindow


class BlurringProcessor(QObject):
    """Video pipeline component for Gaussian blurring on numpy array."""

    arrayChanged = Signal(np.ndarray)

    @Slot(np.ndarray)
    def setArray(self, array: npt.NDArray[np.uint8]):
        self.arrayChanged.emit(cv2.GaussianBlur(array, (0, 0), 25))


class ArraySender(QObject):
    """Object to sent the array to :class:`BlurringProcessor`."""

    arrayChanged = Signal(np.ndarray)


class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._captureSession = NDArrayMediaCaptureSession()
        self._arraySender = ArraySender()
        self._arrayProcessor = BlurringProcessor()
        self._arrayLabel = NDArrayLabel()

        self.captureSession().arrayChanged.connect(self.onArrayPassedFromCamera)
        self._arraySender.arrayChanged.connect(self.arrayProcessor().setArray)
        self.arrayProcessor().arrayChanged.connect(self.arrayLabel().setArray)
        self.arrayLabel().setAlignment(Qt.AlignCenter)  # type: ignore[arg-type]
        self.setCentralWidget(self.arrayLabel())

        camera = QCamera(self)
        self.captureSession().setCamera(camera)
        camera.start()

    def captureSession(self) -> NDArrayMediaCaptureSession:
        return self._captureSession

    def arrayProcessor(self) -> BlurringProcessor:
        return self._arrayProcessor

    def arrayLabel(self) -> NDArrayLabel:
        return self._arrayLabel

    @Slot(np.ndarray)
    def onArrayPassedFromCamera(self, array: npt.NDArray[np.uint8]):
        self._arraySender.arrayChanged.emit(array)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtMultimedia import QCamera
    import sys

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    app.exec()
    app.quit()
