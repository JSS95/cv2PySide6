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
    "QVideoFrame2Array",
    "NDArrayVideoWidget",
    "NDArrayVideoPlayerWidget",
]


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

        self._player = QMediaPlayer()
        self._play_pause_button = QPushButton()
        self._video_slider = ClickableSlider()
        self._video_widget = NDArrayVideoWidget()
        self.initWidgets()
        self.initUI()

        self._pausedBySliderPress = False

    def initWidgets(self):
        self._video_widget.setAlignment(Qt.AlignCenter)

        self._player.playbackStateChanged.connect(self.playbackStateChanged)
        self._player.positionChanged.connect(self.positionChanged)
        self._player.durationChanged.connect(self.durationChanged)
        self._player.setVideoSink(
            self._video_widget.arraySource().frameSource()
        )

        self._play_pause_button.clicked.connect(self.play_pause)

        self._video_slider.valueChanged.connect(self.setPosition)
        self._video_slider.sliderPressed.connect(self.sliderPressed)
        self._video_slider.sliderReleased.connect(self.sliderReleased)

    def initUI(self):
        self._control_layout = QHBoxLayout()
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self._play_pause_button.setIcon(play_icon)
        self._control_layout.addWidget(self._play_pause_button)
        self._video_slider.setOrientation(Qt.Horizontal)
        self._control_layout.addWidget(self._video_slider)

        self._main_layout = QVBoxLayout()
        self._main_layout.addWidget(self._video_widget)
        self._main_layout.addLayout(self._control_layout)
        self.setLayout(self._main_layout)

    def player(self) -> QMediaPlayer:
        return self._player

    def playPauseButton(self) -> QPushButton:
        return self._play_pause_button

    def videoSlider(self) -> ClickableSlider:
        return self._video_slider

    def pausedBySliderPress(self) -> bool:
        """If true, video is paused by pressing slider."""
        return self._pausedBySliderPress

    def setPausedBySliderPress(self, flag: bool):
        self._pausedBySliderPress = flag

    def play_pause(self):
        """Switch play-pause state of media player."""
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self._player.pause()
        else:
            self._player.play()

    def positionChanged(self, position: int):
        """Change the position of video position slider button."""
        self._video_slider.setValue(position)

    def durationChanged(self, duration: int):
        """Change the range of video position slider."""
        self._video_slider.setRange(0, duration)

    def setPosition(self, position: int):
        """Set the position of media player."""
        self._player.setPosition(position)

    def sliderPressed(self):
        """Pause if the video was playing"""
        if self._player.playbackState() == QMediaPlayer.PlayingState:
            self.setPausedBySliderPress(True)
            self._player.pause()

    def sliderReleased(self):
        """Play if the video was paused by :meth:`sliderPressed`"""
        if self._player.playbackState() == QMediaPlayer.PausedState:
            if self.pausedBySliderPress():
                self.setPausedBySliderPress(False)
                self._player.play()

    def playbackStateChanged(self, state: QMediaPlayer.PlaybackState):
        """Change the icon of play-pause button."""
        if state == QMediaPlayer.PlayingState:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self._play_pause_button.setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self._play_pause_button.setIcon(play_icon)

    @Slot()
    def _ensure_stopped(self):
        if self._player.playbackState() != QMediaPlayer.StoppedState:
            self._player.stop()

    def closeEvent(self, event: QCloseEvent):
        self._ensure_stopped()
        event.accept()

    @Slot(str)
    def open(self, path: str):
        """Set the video in path as source, and display first frame."""
        self._ensure_stopped()
        url = QUrl.fromLocalFile(path)
        self._player.setSource(url)

        # Show the first frame. When PySide supports video preview,
        # this can be deleted.
        vidcap = cv2.VideoCapture(path)
        ok, frame = vidcap.read()
        vidcap.release()
        if ok:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self._video_widget.arraySource().setArray(frame_rgb)
