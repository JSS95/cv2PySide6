"""Camera example with Gaussian blurring process."""

import cv2  # type: ignore
from numpy.typing import NDArray
from cv2PySide6 import ArrayProcessor, NDArrayCameraWidget


class BlurringProcessor(ArrayProcessor):
    """
    Video pipeline component for Gaussian blurring on numpy array.
    """

    def processArray(self, array: NDArray) -> NDArray:
        array = super().processArray(array)
        ret = cv2.GaussianBlur(array, (0, 0), 25)
        return ret


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    from PySide6.QtMultimedia import QMediaDevices, QCamera
    import sys

    app = QApplication(sys.argv)
    widget = NDArrayCameraWidget()

    processor = BlurringProcessor()
    widget.setArrayProcessor(processor)

    cameras = QMediaDevices.videoInputs()
    if cameras:
        camera = QCamera(cameras[0])
        widget.mediaCaptureSession().setCamera(camera)
        camera.start()

    widget.show()
    app.exec()
    app.quit()
