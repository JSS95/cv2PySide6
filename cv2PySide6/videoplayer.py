import cv2 # type: ignore
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QPointF, QObject, Signal, Slot, QUrl
from PySide6.QtGui import QMouseEvent, QImage, QCloseEvent
from PySide6.QtWidgets import (QSlider, QStyleOptionSlider, QStyle, QWidget,
    QPushButton, QHBoxLayout, QVBoxLayout)
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QVideoFrame
from qimage2ndarray import rgb_view # type: ignore

from .labels import NDArrayLabel


__all__ = [
    'ClickableSlider',
    'FrameToArrayConverter',
    'ArrayProcessor',
    'NDArrayVideoPlayerWidget',
]


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


class NDArrayVideoPlayerWidget(QWidget):
    """
    Video player widget with play-pause button and position slider.

    ``QVideoFrame`` from :meth:`mediaPlayer` passes
    :meth:`frameToArrayConverter` and then :meth:`arrayProcessor` to
    be processed, and then displayed on :meth:`videoLabel`.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import (get_data_path, NDArrayVideoPlayerWidget)
    >>> vidpath = get_data_path("hello.mp4")
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     player = NDArrayVideoPlayerWidget()
    ...     player.open(vidpath)
    ...     player.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._mediaPlayer = QMediaPlayer()
        self._frameToArrayConverter = FrameToArrayConverter()
        self._arrayProcessor = ArrayProcessor()
        self._playButton = QPushButton()
        self._videoSlider = ClickableSlider()
        self._videoLabel = NDArrayLabel()
        self._pausedBySliderPress = False

        # connect video pipeline
        videoSink = QVideoSink(self)
        self.mediaPlayer().setVideoSink(videoSink)
        videoSink.videoFrameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        self.connectArrayProcessor()
        # connect other signals
        self.playButton().clicked.connect(self.onPlayButtonClicked)
        self.videoSlider().sliderPressed.connect(self.onSliderPress)
        self.videoSlider().sliderReleased.connect(self.onSliderRelease)
        self.videoSlider().valueChanged.connect(self.onSliderValueChange)
        self.mediaPlayer().playbackStateChanged.connect(
            self.onPlaybackStateChange
        )
        self.mediaPlayer().sourceChanged.connect(self.onMediaSourceChange)
        self.mediaPlayer().positionChanged.connect(self.onMediaPositionChange)
        self.mediaPlayer().durationChanged.connect(self.onMediaDurationChange)
        self.videoLabel().setAlignment(Qt.AlignCenter)

        self.initUI()

    def initUI(self):
        control_layout = QHBoxLayout()
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.playButton().setIcon(play_icon)
        control_layout.addWidget(self.playButton())
        self.videoSlider().setOrientation(Qt.Horizontal)
        control_layout.addWidget(self.videoSlider())

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def mediaPlayer(self) -> QMediaPlayer:
        """
        Media player to produce ``QVideoFrame`` stream from local file
        and provide to :meth:`frameToArrayConverter`.
        """
        return self._mediaPlayer

    def frameToArrayConverter(self) -> FrameToArrayConverter:
        """
        Converts ``QVideoFrame`` from video sink of :meth:`mediaPlayer`
        to numpy array and provide to :meth:`arrayProcessor`.
        """
        return self._frameToArrayConverter

    def arrayProcessor(self) -> ArrayProcessor:
        """
        Process the array from :meth:`frameToArrayConverter` and provide
        to :meth:`videoLabel`.
        """
        return self._arrayProcessor

    def setArrayProcessor(self, processor: ArrayProcessor):
        """
        Change :meth:`arrayProcessor` and update signal connections.
        """
        self.disconnectArrayProcessor()
        self._arrayProcessor = processor
        self.connectArrayProcessor()

    def connectArrayProcessor(self):
        """
        Connect signals to and slots from :meth:`arrayProcessor`.
        """
        self.frameToArrayConverter().arrayChanged.connect(
            self.arrayProcessor().setArray
        )
        self.arrayProcessor().arrayChanged.connect(
            self.videoLabel().setArray
        )

    def disconnectArrayProcessor(self):
        """
        Discoonnect signals to and slots from :meth:`arrayProcessor`.
        """
        self.frameToArrayConverter().arrayChanged.disconnect(
            self.arrayProcessor().setArray
        )
        self.arrayProcessor().arrayChanged.disconnect(
            self.videoLabel().setArray
        )

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    def playButton(self) -> QPushButton:
        return self._playButton

    def videoSlider(self) -> ClickableSlider:
        return self._videoSlider

    def pausedBySliderPress(self) -> bool:
        """If true, video is paused by pressing slider."""
        return self._pausedBySliderPress

    @Slot()
    def onPlayButtonClicked(self):
        """Switch play-pause state of media player."""
        if self.mediaPlayer().playbackState() == QMediaPlayer.PlayingState:
            self.mediaPlayer().pause()
        else:
            self.mediaPlayer().play()

    @Slot()
    def onSliderPress(self):
        """Pause if the video was playing."""
        if self.mediaPlayer().playbackState() == QMediaPlayer.PlayingState:
            self._pausedBySliderPress = True
            self.mediaPlayer().pause()

    @Slot()
    def onSliderRelease(self):
        """Play if the video was paused by :meth:`onSliderPress`."""
        if self.mediaPlayer().playbackState() == QMediaPlayer.PausedState:
            if self.pausedBySliderPress():
                self._pausedBySliderPress = False
                self.mediaPlayer().play()

    @Slot(int)
    def onSliderValueChange(self, position: int):
        """Set the position of media player."""
        self.mediaPlayer().setPosition(position)

    @Slot(QMediaPlayer.PlaybackState)
    def onPlaybackStateChange(self, state: QMediaPlayer.PlaybackState):
        """Change the icon of play-pause button."""
        if state == QMediaPlayer.PlayingState:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self.playButton().setIcon(pause_icon)
            self.frameToArrayConverter().setIgnoreNullFrame(True)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self.playButton().setIcon(play_icon)
            self.frameToArrayConverter().setIgnoreNullFrame(False)

    @Slot(QUrl)
    def onMediaSourceChange(self, source: QUrl):
        """Display the first frame of the media."""
        # Delete this when PySide6 supports video preview
        vidcap = cv2.VideoCapture(source.toLocalFile())
        ok, frame = vidcap.read()
        vidcap.release()
        if ok:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.arrayProcessor().setArray(frame_rgb)

    @Slot(int)
    def onMediaPositionChange(self, position: int):
        """Change the position of video position slider button."""
        self.videoSlider().setValue(position)

    @Slot(int)
    def onMediaDurationChange(self, duration: int):
        """Change the range of video position slider."""
        self.videoSlider().setRange(0, duration)

    def open(self, path: str):
        """Set the video in path as source, and display first frame."""
        self.mediaPlayer().stop()
        url = QUrl.fromLocalFile(path)
        self.mediaPlayer().setSource(url)

    def closeEvent(self, event: QCloseEvent):
        """Stop :meth:`mediaPlayer` before closing."""
        self.mediaPlayer().stop()
        event.accept()
