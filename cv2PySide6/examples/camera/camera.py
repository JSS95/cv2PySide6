"""Camera example with Gaussian blurring process."""

import cv2 # type: ignore
from numpy.typing import NDArray
from cv2PySide6 import ArrayProcessor, NDArrayVideoWidget


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
    from PySide6.QtMultimedia import (QMediaCaptureSession, QMediaDevices,
        QCamera, QVideoSink)
    from cv2PySide6 import FrameToArrayConverter
    import sys

    app = QApplication(sys.argv)
    player = NDArrayVideoWidget()
    processor = BlurringProcessor()
    player.setArrayProcessor(processor)

    captureSession = QMediaCaptureSession()
    cameras = QMediaDevices.videoInputs()
    if cameras:
        # construct video pipeline: camera -> captureSession
        # -> videoSink -> converter -> processor (-> label in player)
        camera = QCamera(cameras[0])
        videoSink = QVideoSink()
        converter = FrameToArrayConverter()
        captureSession.setCamera(camera)
        captureSession.setVideoSink(videoSink)
        videoSink.videoFrameChanged.connect(
            converter.setVideoFrame
        )
        converter.arrayChanged.connect(processor.setArray)

        camera.start()

    player.show()
    app.exec()
    app.quit()
