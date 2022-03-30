"""
Utility objects for video widgets.
"""

import cv2 # type: ignore
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QPointF, QObject, Signal, Slot, QThread
from PySide6.QtGui import QMouseEvent, QImage
from PySide6.QtWidgets import QSlider, QStyleOptionSlider, QStyle
from PySide6.QtMultimedia import QVideoFrame
from qimage2ndarray import rgb_view # type: ignore
from typing import Union


__all__ = [
    'ArrayProcessor',
    'FrameToArrayConverter',
    'ClickableSlider',
    'CV2VideoPlayer',
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
    """
    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._ignoreNullFrame = True

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

    @staticmethod
    def convertQImageToArray(qimg: QImage) -> NDArray:
        """
        Convert *qimg* to numpy array. Null image is converted to
        empty array.
        """
        if not qimg.isNull():
            array = rgb_view(qimg)
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
        gr = self.style().subControlRect(QStyle.CC_Slider,
                                         opt,
                                         QStyle.SC_SliderGroove,
                                         self)
        sr = self.style().subControlRect(QStyle.CC_Slider,
                                         opt,
                                         QStyle.SC_SliderHandle,
                                         self)

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
        return QStyle.sliderValueFromPosition(self.minimum(),
                                              self.maximum(),
                                              int(p - sliderMin),
                                              sliderMax - sliderMin,
                                              opt.upsideDown)


class CV2VideoPlayer(QThread):
    """
    Thread object to grab frame from local video file using
    ``cv2.VideoCapture``. This class mimics ``QMediaPlayer``.

    Passing video path to :meth:`setSource` sets :meth:`videoCapture`.
    It emits the path to :attr:`sourceChanged` and total number of
    frames to :attr:`durationChanged`.

    :meth:`setPosition` sets the current frame position of
    :meth:`videoCapture`.
    """
    sourceChanged = Signal(str)
    durationChanged = Signal(int)
    positionChanged = Signal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoCapture = None

    def videoCapture(self) -> Union[cv2.VideoCapture, None]:
        return self._videoCapture

    def duration(self) -> int:
        """Total number of frames in :meth:`videoCapture`."""
        cap = self.videoCapture()
        if cap is None:
            ret = 0
        else:
            ret = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        return ret

    def position(self) -> int:
        """Current frame number of :meth:`videoCapture`."""
        cap = self.videoCapture()
        if cap is None:
            ret = 0
        else:
            ret = cap.get(cv2.CAP_PROP_POS_FRAMES)
        return ret

    def setSource(self, path: str):
        """Update :meth:`videoCapture` with *path*."""
        self._videoCapture = cv2.VideoCapture(path)
        self.sourceChanged.emit(path)
        self.durationChanged.emit(self.duration())
        self.positionChanged.emit(0)

    def setPosition(self, pos: int):
        """Self *pos* as current frame of :meth:`videoCapture`."""
        cap = self.videoCapture()
        if cap is not None:
            currentpos = cap.get(cv2.CAP_PROP_POS_FRAMES)
            cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
            if currentpos != pos:
                self.positionChanged.emit(pos)
