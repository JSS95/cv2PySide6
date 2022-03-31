"""
Utility objects for video widgets.
"""

import cv2 # type: ignore
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QPointF, QObject, Signal, Slot, QThread, QTimer
from PySide6.QtGui import QMouseEvent, QImage
from PySide6.QtWidgets import QSlider, QStyleOptionSlider, QStyle
from PySide6.QtMultimedia import QVideoFrame, QMediaPlayer
from qimage2ndarray import rgb_view # type: ignore
import queue
from typing import Union


__all__ = [
    'ArrayProcessor',
    'FrameToArrayConverter',
    'ClickableSlider',
    'CV2VideoReader',
    'CV2VideoRetriever',
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


class CV2VideoReader(QThread):
    """
    Thread to produce frames from video file using ``cv2.VideoCapture``.

    Frames from :meth:`videoCapture` are stored to :meth:`frameBuffer`
    so that consumer can retrieve them.

    """
    durationChanged = Signal(int)
    positionChanged = Signal(int)
    videoReadFinished = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoCapture = None
        self._frameBuffer = queue.Queue()

    def videoCapture(self) -> Union[cv2.VideoCapture, None]:
        return self._videoCapture

    def frameBuffer(self) -> queue.Queue:
        return self._frameBuffer

    def setFrameBuffer(self, buffer: queue.Queue):
        self._frameBuffer = buffer

    def duration(self) -> int:
        """Total number of frames in :meth:`videoCapture`."""
        cap = self.videoCapture()
        if cap is None:
            ret = 0
        else:
            ret = cap.get(cv2.CAP_PROP_FRAME_COUNT)
        return ret

    def fps(self) -> float:
        """FPS of :meth:`videoCapture`."""
        cap = self.videoCapture()
        if cap is None:
            ret = float(0)
        else:
            ret = cap.get(cv2.CAP_PROP_FPS)
        return ret

    def position(self) -> int:
        """Current frame number of :meth:`videoCapture`."""
        cap = self.videoCapture()
        if cap is None:
            pos = 0
        else:
            pos = cap.get(cv2.CAP_PROP_POS_FRAMES)
        ret = int(pos - self.frameBuffer().qsize())
        return ret

    def setSource(self, path: str):
        """Update :meth:`videoCapture` with *path*."""
        old_cap = self.videoCapture()
        if old_cap is not None:
            old_cap.release()
        self._videoCapture = cv2.VideoCapture(path)
        self.durationChanged.emit(self.duration())
        self.positionChanged.emit(0)

    def setPosition(self, pos: int):
        """Set current frame position to *pos*."""
        cap = self.videoCapture()
        if cap is not None:
            currentpos = cap.get(cv2.CAP_PROP_POS_FRAMES)
            if currentpos != pos:
                with self.frameBuffer().mutex:
                    self.frameBuffer().queue.clear()
                cap.set(cv2.CAP_PROP_POS_FRAMES, pos)
                self.positionChanged.emit(pos)

    def run(self):
        self._alive = True
        while self._alive:
            if self.videoCapture() is None:
                continue
            ok, img = self.videoCapture().read()
            if ok:
                while self._alive:
                    if not self.frameBuffer().full():
                        self.frameBuffer().put_nowait(img)
                        break
            else:
                self._alive = False
        self.videoReadFinished.emit()

    def pause(self):
        self._alive = False
        self.wait()

    def quit(self):
        self.pause()
        super().quit()


class CV2VideoRetriever(QObject):
    """
    Consumer object to emit frames.

    Whenever :meth:`timer` triggers, this object tries to take frame
    from :meth:`frameBuffer` and emit to :attr:`arrayChanged`.

    """
    playbackFinished = Signal()
    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frameBuffer = queue.Queue()
        self._timer = QTimer(self)
        self._noMoreFrameComing = False

        self.timer().timeout.connect(self.retrieveFrame)

    def frameBuffer(self) -> queue.Queue:
        """Queue where the frame array are retrieved from."""
        return self._frameBuffer

    def timer(self) -> QTimer:
        return self._timer

    def setFrameBuffer(self, buffer: queue.Queue):
        self._frameBuffer = buffer

    def startTimer(self, interval: int):
        self.timer().start(interval)

    def stopTimer(self):
        self.timer().stop()

    @Slot()
    def retrieveFrame(self):
        if self.frameBuffer().empty() and self._noMoreFrameComing:
            self.pause()
            self.playbackFinished.emit()
        else:
            frame = self.frameBuffer().get()
            self.arrayChanged.emit(frame)

    @Slot()
    def preparePlaybackFinish(self):
        self._noMoreFrameComing = True

    def pause(self):
        self.stopTimer()

    def quit(self):
        self.pause()
        super().quit()


class CV2VideoPlayer(QObject):
    """
    Object to produce video stream with ``cv2.VideoCapture``. This class
    emulates ``QMediaPlayer``.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import CV2VideoPlayer, get_data_path
    >>> def runPlayer():
    ...     app = QApplication(sys.argv)
    ...     player = CV2VideoPlayer(app)
    ...     player.setSource(get_data_path('hello.mp4'))
    ...     player.play()
    ...     app.exec()
    ...     app.quit()
    >>> runPlayer() # doctest: +SKIP
    """
    PlaybackState = QMediaPlayer.PlaybackState
    StoppedState = QMediaPlayer.StoppedState
    PlayingState = QMediaPlayer.PlayingState
    PausedState = QMediaPlayer.PausedState

    arrayChanged = Signal(np.ndarray)
    sourceChanged = Signal(str)
    durationChanged = Signal(int)
    positionChanged = Signal(int)
    playbackStateChanged = Signal(PlaybackState)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._videoReader = CV2VideoReader(self)
        self._videoRetriever = CV2VideoRetriever(self)
        self._frameBuffer = queue.Queue(10)
        self._playbackState = self.StoppedState

        self.videoReader().setFrameBuffer(self.frameBuffer())
        self.videoRetriever().setFrameBuffer(self.frameBuffer())
        self.videoReader().durationChanged.connect(self.durationChanged)
        self.videoReader().positionChanged.connect(self.positionChanged)
        self.videoReader().videoReadFinished.connect(
            self.videoRetriever().preparePlaybackFinish
        )
        self.videoRetriever().playbackFinished.connect(self.stop)
        self.videoRetriever().arrayChanged.connect(self.arrayChanged)

    def videoReader(self) -> CV2VideoReader:
        return self._videoReader

    def videoRetriever(self) -> CV2VideoRetriever:
        return self._videoRetriever

    def frameBuffer(self) -> queue.Queue:
        return self._frameBuffer

    def playbackState(self) -> PlaybackState:
        return self._playbackState

    def setFrameBuffer(self, buffer: queue.Queue):
        self._frameBuffer = buffer
        self.videoReader().setFrameBuffer(self.frameBuffer())
        self.videoRetriever().setFrameBuffer(self.frameBuffer())

    @Slot()
    def play(self):
        self.videoReader().start()
        fps = self.videoReader().fps()
        if fps != 0:
            self.videoRetriever().startTimer(int(1000/fps))

        self._playbackState = self.PlayingState
        self.playbackStateChanged.emit(self.playbackState())

    @Slot()
    def pause(self):
        self.videoReader().pause()
        self.videoRetriever().pause()
        self._playbackState = self.PausedState
        self.playbackStateChanged.emit(self.playbackState())

    @Slot()
    def stop(self):
        self.videoReader().pause()
        self.videoRetriever().pause()
        self.videoReader().setPosition(0)
        self._playbackState = self.StoppedState
        self.playbackStateChanged.emit(self.playbackState())

    @Slot(str)
    def setSource(self, source: str):
        self.stop()
        self.videoReader().setSource(source)
        self.sourceChanged.emit(source)

    @Slot(int)
    def setPosition(self, pos: int):
        self.videoReader().setPosition(pos)
