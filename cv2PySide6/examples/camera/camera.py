"""Camera example with Gaussian blurring process."""

import cv2  # type: ignore
from cv2PySide6 import NDArrayMediaCaptureSession, NDArrayLabel
import numpy as np
import numpy.typing as npt
from PySide6.QtCore import QObject, Signal, Qt


class BlurringProcessor(QObject):
    """
    Video pipeline component for Gaussian blurring on numpy array.
    """

    arrayChanged = Signal(np.ndarray)

    def setArray(self, array: npt.NDArray[np.uint8]):
        self.arrayChanged.emit(cv2.GaussianBlur(array, (0, 0), 25))


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtMultimedia import QCamera
    import sys

    app = QApplication(sys.argv)

    session = NDArrayMediaCaptureSession()
    processor = BlurringProcessor()
    label = NDArrayLabel()

    session.arrayChanged.connect(processor.setArray)
    processor.arrayChanged.connect(label.setArray)
    label.setAlignment(Qt.AlignCenter)  # type: ignore[arg-type]

    camera = QCamera()
    session.setCamera(camera)
    camera.start()

    label.show()
    app.exec()
    app.quit()
