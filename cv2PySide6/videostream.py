"""
Utility objects for video widgets.
"""
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtGui import QImage
from PySide6.QtMultimedia import (
    QVideoFrame,
    QMediaPlayer,
    QVideoSink,
    QMediaCaptureSession,
)
from qimage2ndarray import rgb_view  # type: ignore[import]
from typing import Callable


__all__ = [
    "FrameToArrayConverter",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
]


class FrameToArrayConverter(QObject):
    """
    Video pipeline component which converts ``QVideoFrame`` to numpy array and
    emits to :attr:`arrayChanged`.

    ``QVideoFrame`` is first transformed to ``QImage`` and then converted by
    :meth:`converter`. You can change the converter by :meth:`setConverter`.

    Null frame does not emit array by default. If you set :meth:`ignoreNullFrame`
    to False, three-dimensional empty array will be emitted.

    """

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ignoreNullFrame = True
        self._converter = rgb_view

    def ignoreNullFrame(self) -> bool:
        """
        If True, null ``QVideoFrame`` passed to :meth:`setVideoFrame` will be
        ignored.
        """
        return self._ignoreNullFrame

    @Slot(bool)
    def setIgnoreNullFrame(self, ignore: bool):
        """Update :meth:`ignoreNullFrame`."""
        self._ignoreNullFrame = ignore

    @Slot(QVideoFrame)
    def setVideoFrame(self, frame: QVideoFrame):
        """
        Convert ``QVideoFrame`` to :class:`numpy.ndarray` and emit to
        :meth:`setArray`.
        """
        qimg = frame.toImage()
        if qimg.isNull() and self.ignoreNullFrame():
            pass
        else:
            array = self.convertQImageToArray(qimg)
            self.arrayChanged.emit(array)

    def converter(self) -> Callable[[QImage], NDArray]:
        """
        A callable to convert ``QImage`` instance to numpy array. Default is
        ``qimage2.ndarray.rgb_view``.
        """
        return self._converter

    def setConverter(self, func: Callable[[QImage], NDArray]):
        self._converter = func

    def convertQImageToArray(self, qimg: QImage) -> NDArray:
        """
        Convert *qimg* to numpy array. Null image is converted to empty array.
        """
        if not qimg.isNull():
            array = self.converter()(qimg)
        else:
            array = np.empty((0, 0, 0))
        return array


class NDArrayVideoPlayer(QMediaPlayer):
    """
    Minimal implementation of video player which emits frames as numpy arrays to
    :attr:`arrayChanged` signal.
    """

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame2Arr = FrameToArrayConverter(self)

        self.setVideoSink(QVideoSink(self))
        self.videoSink().videoFrameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        self.frameToArrayConverter().arrayChanged.connect(self.arrayChanged)

    def frameToArrayConverter(self) -> FrameToArrayConverter:
        return self._frame2Arr


class NDArrayMediaCaptureSession(QMediaCaptureSession):
    """
    Minimal implementation of media capture session which emits frames as
    numpy arrays to :attr:`arrayChanged` signal.
    """

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame2Arr = FrameToArrayConverter(self)

        self.setVideoSink(QVideoSink(self))
        self.videoSink().videoFrameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        self.frameToArrayConverter().arrayChanged.connect(self.arrayChanged)

    def frameToArrayConverter(self) -> FrameToArrayConverter:
        return self._frame2Arr
