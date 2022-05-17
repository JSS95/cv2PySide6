"""
Utility objects for video widgets.
"""

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QPointF, QObject, Signal, Slot
from PySide6.QtGui import QMouseEvent, QImage
from PySide6.QtWidgets import QSlider, QStyleOptionSlider, QStyle
from PySide6.QtMultimedia import (
    QVideoFrame,
    QMediaPlayer,
    QVideoSink,
    QMediaCaptureSession,
)
from qimage2ndarray import rgb_view  # type: ignore
from typing import Callable


__all__ = [
    "ArrayProcessor",
    "FrameToArrayConverter",
    "ClickableSlider",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
]


class ArrayProcessor(QObject):
    """
    Video pipeline object to process numpy array and emit to
    :attr:`arrayChanged`.
    """

    arrayChanged = Signal(np.ndarray)

    @Slot(np.ndarray)
    def setArray(self, array: NDArray):
        """
        Process *array* with :meth:`processArray` and emit to
        :attr:`arrayChanged`.
        """
        self.arrayChanged.emit(self.processArray(array))

    def processArray(self, array: NDArray):
        """Process and return *array*."""
        return array


class FrameToArrayConverter(QObject):
    """
    Video pipeline component which converts ``QVideoFrame`` to numpy
    array and emits to :attr:`arrayChanged`.

    ``QVideoFrame`` is first transformed to ``QImage`` and then
    converted by :meth:`converter`. You can change the converter by
    :meth:`setConverter`.

    Null frame does not emit array by default. If you set
    :meth:`ignoreNullFrame` to False, three-dimensional empty array will
    be emitted.

    """

    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ignoreNullFrame = True
        self._converter = rgb_view

    def ignoreNullFrame(self) -> bool:
        """
        If True, null ``QVideoFrame`` passed to :meth:`setVideoFrame`
        will be ignored.
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
        A callable to convert ``QImage`` instance to numpy array.
        Default is ``qimage2.ndarray.rgb_view``.
        """
        return self._converter

    def setConverter(self, func: Callable[[QImage], NDArray]):
        self._converter = func

    def convertQImageToArray(self, qimg: QImage) -> NDArray:
        """
        Convert *qimg* to numpy array. Null image is converted to
        empty array.
        """
        if not qimg.isNull():
            array = self.converter()(qimg)
        else:
            array = np.empty((0, 0, 0))
        return array


class ClickableSlider(QSlider):
    """``QSlider`` whose groove can be clicked to move to position."""

    # https://stackoverflow.com/questions/52689047
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            val = self.pixelPosToRangeValue(event.position())
            self.setValue(val)
        super().mousePressEvent(event)

    def pixelPosToRangeValue(self, pos: QPointF) -> int:
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        gr = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderGroove, self
        )
        sr = self.style().subControlRect(
            QStyle.CC_Slider, opt, QStyle.SC_SliderHandle, self
        )

        if self.orientation() == Qt.Horizontal:
            sliderLength = sr.width()
            sliderMin = gr.x()
            sliderMax = gr.right() - sliderLength + 1
        else:
            sliderLength = sr.height()
            sliderMin = gr.y()
            sliderMax = gr.bottom() - sliderLength + 1
        pr = pos - sr.center() + sr.topLeft()
        p = pr.x() if self.orientation() == Qt.Horizontal else pr.y()
        return QStyle.sliderValueFromPosition(
            self.minimum(),
            self.maximum(),
            int(p - sliderMin),
            sliderMax - sliderMin,
            opt.upsideDown,  # type: ignore[attr-defined]
        )


class NDArrayVideoPlayer(QMediaPlayer):
    """
    Video player which emits frames as numpy arrays to
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
    Media capture session which emits frames from camera as numpy arrays
    to :attr:`arrayChanged` signal.
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
