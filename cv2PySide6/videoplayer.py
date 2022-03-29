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
    'FrameToArrayConverter',
    'NDArrayVideoPlayerWidget',
]


class FrameToArrayConverter(QObject):
    """
    Video pipeline component which converts ``QVideoFrame`` to numpy
    array and emits to :attr:`arrayChanged`.
    """
    arrayChanged = Signal(np.ndarray)

    @Slot(QVideoFrame)
    def setVideoFrame(self, frame: QVideoFrame):
        """
        Convert ``QVideoFrame`` to ``QImage``, then to
        :class:`numpy.ndarray`. Pass it to :meth:`setArray`.
        """
        qimg = frame.toImage()
        if not qimg.isNull():
            array = rgb_view(qimg)
        else:
            array = np.empty((0, 0, 0))
        self.arrayChanged.emit(array)


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
        self._arraySource = FrameToArrayConverter()
        self._playButton = QPushButton()
        self._videoSlider = ClickableSlider()
        self._videoLabel = NDArrayLabel()
        self._pausedBySliderPress = False

        # connect video pipeline
        videoSink = QVideoSink(self)
        self.mediaPlayer().setVideoSink(videoSink)
        videoSink.videoFrameChanged.connect(self.arraySource().setVideoFrame)
        self.arraySource().arrayChanged.connect(self.videoLabel().setArray)
        # connect other signals
        self.mediaPlayer().playbackStateChanged.connect(
            self.onPlaybackStateChange
        )
        self.mediaPlayer().positionChanged.connect(self.onMediaPositionChange)
        self.mediaPlayer().durationChanged.connect(self.onMediaDurationChange)
        self.playButton().clicked.connect(self.onPlayButtonClicked)
        self.videoSlider().valueChanged.connect(self.onSliderValueChange)
        self.videoSlider().sliderPressed.connect(self.onSliderPress)
        self.videoSlider().sliderReleased.connect(self.onSliderRelease)
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
        return self._mediaPlayer

    def arraySource(self) -> FrameToArrayConverter:
        return self._arraySource

    def playButton(self) -> QPushButton:
        return self._playButton

    def videoSlider(self) -> ClickableSlider:
        return self._videoSlider

    def videoLabel(self) -> NDArrayLabel:
        return self._videoLabel

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
            self.videoLabel().setArray(frame_rgb)
