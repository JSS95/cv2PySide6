import cv2 # type: ignore
import numpy as np
from PySide6.QtCore import Qt, QObject, Signal, Slot, QUrl
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QWidget, QPushButton, QStyle, QHBoxLayout,
    QVBoxLayout)
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink, QVideoFrame
from qimage2ndarray import rgb_view # type: ignore

from .labels import NDArrayLabel
from .utilwidgets import ClickableSlider


__all__ = [
    'QVideoFrameToArrayConverter',
    'QVideoFrame2Array',
    'NDArrayVideoWidget',
    'NDArrayVideoPlayerWidget',
]


class QVideoFrameToArrayConverter(QVideoSink):
    """
    Video sink which converts ``QVideoFrame`` to numpy array and emits
    to :attr:`arrayChanged`.
    """
    arrayChanged = Signal(np.ndarray)

    @staticmethod
    def convertQVideoFrameToArray(self, frame: QVideoFrame):
        """Converts *frame* to numpy array."""
        qimg = frame.toImage()
        if not qimg.isNull():
            array = rgb_view(qimg)
        else:
            array = np.empty((0, 0, 0))
        return array

    @Slot(QVideoFrame)
    def setVideoFrame(self, frame: QVideoFrame):
        super().setVideoFrame(frame)
        array = self.convertQVideoFrameToArray(frame)
        self.arrayChanged.emit(array)


class QVideoFrame2Array(QObject):
    """
    Class to convert ``QVideoFrame`` to :class:`numpy.ndarray`, perform
    image processing, then emit.

    This class acquires ``QVideoFrame`` from :meth:`frameSource` via
    :meth:`setVideoFrame` slot. Then it converts it to
    :class:`numpy.ndarray`, process with :meth:`processArray`, and emit
    via :attr:`arrayChanged` signal. 

    """
    arrayChanged = Signal(np.ndarray)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._frame_source = QVideoSink()

        self._frame_source.videoFrameChanged.connect(self.setVideoFrame)

    def frameSource(self) -> QVideoSink:
        """Upstream source which provides ``QVideoFrame``."""
        return self._frame_source

    @Slot(QVideoFrame)
    def setVideoFrame(self, frame: QVideoFrame):
        """
        Convert ``QVideoFrame`` to ``QImage``, then to
        :class:`numpy.ndarray`. Pass it to :meth:`setArray`.
        """
        qimg = frame.toImage()
        if not qimg.isNull():
            array = rgb_view(qimg)
            self.setArray(array)

    def setArray(self, array: np.ndarray):
        """
        Update :meth:`array`, and emit processed array to
        :attr:`arrayChanged`.

        See Also
        ========

        processArray

        """
        self.arrayChanged.emit(self.processArray(array))

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """Process and return *array*. Subclass may override this."""
        return array


class NDArrayVideoWidget(NDArrayLabel):
    """
    A scalable label which can receive and display video frame in
    :class:`numpy.ndarray` format from :meth:`arraySource`.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setArraySource(QVideoFrame2Array())

    def arraySource(self) -> QVideoFrame2Array:
        """
        Upstream source which provides frame in :class:`numpy.ndarray`.
        """
        return self._array_source

    def setArraySource(self, source: QVideoFrame2Array):
        self._array_source = source
        self._array_source.arrayChanged.connect(self.setArray)


class NDArrayVideoPlayerWidget(QWidget):
    """
    Video player widget with play-pause button and position slider.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import (get_data_path, NDArrayVideoPlayerWidget)
    >>> vidpath = get_data_path("hello.mp4")
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     player = NDArrayVideoPlayerWidget()
    ...     geometry = player.screen().availableGeometry()
    ...     player.resize(geometry.width() / 3, geometry.height() / 2)
    ...     player.open(vidpath)
    ...     player.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._mediaPlayer = QMediaPlayer()
        self._playButton = QPushButton()
        self._videoSlider = ClickableSlider()
        self._video_widget = NDArrayVideoWidget()
        self.initWidgets()
        self.initUI()

        self._pausedBySliderPress = False

    def initWidgets(self):
        self._video_widget.setAlignment(Qt.AlignCenter)

        self.mediaPlayer().playbackStateChanged.connect(self.onPlaybackStateChange)
        self.mediaPlayer().positionChanged.connect(self.onMediaPositionChange)
        self.mediaPlayer().durationChanged.connect(self.onMediaDurationChange)
        self.mediaPlayer().setVideoSink(
            self._video_widget.arraySource().frameSource()
        )

        self.playButton().clicked.connect(self.onPlayButtonClicked)

        self.videoSlider().valueChanged.connect(self.onSliderValueChange)
        self.videoSlider().sliderPressed.connect(self.onSliderPress)
        self.videoSlider().sliderReleased.connect(self.onSliderRelease)

    def initUI(self):
        control_layout = QHBoxLayout()
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.playButton().setIcon(play_icon)
        control_layout.addWidget(self.playButton())
        self.videoSlider().setOrientation(Qt.Horizontal)
        control_layout.addWidget(self.videoSlider())

        layout = QVBoxLayout()
        layout.addWidget(self._video_widget)
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def mediaPlayer(self) -> QMediaPlayer:
        return self._mediaPlayer

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

    @Slot(int)
    def onMediaPositionChange(self, position: int):
        """Change the position of video position slider button."""
        self.videoSlider().setValue(position)

    @Slot(int)
    def onMediaDurationChange(self, duration: int):
        """Change the range of video position slider."""
        self.videoSlider().setRange(0, duration)

    def onSliderValueChange(self, position: int):
        """Set the position of media player."""
        self.mediaPlayer().setPosition(position)

    def onSliderPress(self):
        """Pause if the video was playing."""
        if self.mediaPlayer().playbackState() == QMediaPlayer.PlayingState:
            self._pausedBySliderPress = True
            self.mediaPlayer().pause()

    def onSliderRelease(self):
        """Play if the video was paused by :meth:`onSliderPress`."""
        if self.mediaPlayer().playbackState() == QMediaPlayer.PausedState:
            if self.pausedBySliderPress():
                self._pausedBySliderPress = False
                self.mediaPlayer().play()

    @Slot(QMediaPlayer.PlaybackState)
    def onPlaybackStateChange(self, state: QMediaPlayer.PlaybackState):
        """Change the icon of play-pause button."""
        if state == QMediaPlayer.PlayingState:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self.playButton().setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self.playButton().setIcon(play_icon)

    def closeEvent(self, event: QCloseEvent):
        self.mediaPlayer().stop()
        event.accept()

    @Slot(str)
    def open(self, path: str):
        """Set the video in path as source, and display first frame."""
        self.mediaPlayer().stop()
        url = QUrl.fromLocalFile(path)
        self.mediaPlayer().setSource(url)

        # Show the first frame. When PySide supports video preview,
        # this can be deleted.
        vidcap = cv2.VideoCapture(path)
        ok, frame = vidcap.read()
        vidcap.release()
        if ok:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self._video_widget.arraySource().setArray(frame_rgb)
