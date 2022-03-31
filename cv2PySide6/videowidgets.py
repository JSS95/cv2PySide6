"""
Widgets to play video stream.
"""

import cv2 # type: ignore
import numpy as np
import numpy.typing as NDArray
from PySide6.QtCore import Qt, Slot, QUrl
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStyle,
    QPushButton)
from PySide6.QtMultimedia import QMediaPlayer, QVideoSink

from .labels import NDArrayLabel
from .videoutil import (ClickableSlider, FrameToArrayConverter, ArrayProcessor,
    NDArrayVideoPlayer)
from .typing import ArrayProcessorProtocol, VideoPlayControllerProtocol


__all__ = [
    'NDArrayVideoWidget',
    'NDArrayVideoSeekerWidget',
    'NDArrayVideoPlayerWidget',
]


class NDArrayVideoWidget(QWidget):
    """
    Widget to display video from numpy arrays.

    Examples
    ========

    In this example, video pipeline of ``mediaPlayer -> videoSink ->
    frame2Arr -> arrayProcessor`` is established to play video file.

    >>> from PySide6.QtCore import QUrl
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import get_data_path, NDArrayVideoWidget
    >>> vidpath = get_data_path('hello.mp4')
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     w = NDArrayVideoWidget()
    ...     w.videoPlayer().setSource(QUrl.fromLocalFile(vidpath))
    ...     w.show()
    ...     w.videoPlayer().play()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = NDArrayVideoPlayer()
        self._arrayProcessor = ArrayProcessor()
        self._videoLabel = NDArrayLabel()

        self.connectVideoPlayer()
        self.connectArrayProcessor()
        self.videoLabel().setAlignment(Qt.AlignCenter)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        self.setLayout(layout)

    def videoPlayer(self) -> NDArrayVideoPlayer:
        return self._videoPlayer

    def setVideoPlayer(self, player: NDArrayVideoPlayer):
        self.disconnectVideoPlayer()
        self._videoPlayer = player
        self.connectVideoPlayer()

    def connectVideoPlayer(self):
        self.__processConnection = self.videoPlayer().arrayChanged.connect(
            self.onArrayPassedFromPlayer
        )

    def disconnectVideoPlayer(self):
        self.videoPlayer().arrayChanged.disconnect(
            self.__processConnection
        )

    def arrayProcessor(self) -> ArrayProcessorProtocol:
        """Process the array and provide to :meth:`videoLabel`."""
        return self._arrayProcessor

    def setArrayProcessor(self, processor: ArrayProcessorProtocol):
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
        self.__displayConnection = self.arrayProcessor().arrayChanged.connect(
            self.videoLabel().setArray
        )

    def disconnectArrayProcessor(self):
        """
        Discoonnect signals to and slots from :meth:`arrayProcessor`.
        """
        self.arrayProcessor().arrayChanged.disconnect(
            self.__displayConnection
        )

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    @Slot(np.ndarray)
    def onArrayPassedFromPlayer(self, array: NDArray):
        self.arrayProcessor().setArray(array)


class NDArrayVideoSeekerWidget(NDArrayVideoWidget):
    """
    Widget to display and seek video from numpy arrays.

    Video position can be seek by controlling :meth:`videoSlider`.

    Examples
    ========

    >>> from PySide6.QtCore import QUrl
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import get_data_path, NDArrayVideoSeekerWidget
    >>> vidpath = get_data_path('hello.mp4')
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     w = NDArrayVideoSeekerWidget()
    ...     w.videoPlayer().setSource(QUrl.fromLocalFile(vidpath))
    ...     w.show()
    ...     w.videoPlayer().play()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """
    def __init__(self, parent=None):
        self._videoSlider = ClickableSlider()
        super().__init__(parent)

        self.videoSlider().valueChanged.connect(self.onSliderValueChange)

    def initUI(self):
        super().initUI()
        self.videoSlider().setOrientation(Qt.Horizontal)
        self.layout().addWidget(self.videoSlider())

    def connectVideoPlayer(self):
        super().connectVideoPlayer()
        self.__positionConnection = self.videoPlayer().positionChanged.connect(
            self.onMediaPositionChange
        )
        self.__durationConnection = self.videoPlayer().durationChanged.connect(
            self.onMediaDurationChange
        )

    def disconnectVideoPlayer(self):
        super().disconnectVideoPlayer()
        self.videoPlayer().positionChanged.disconnect(
            self.__positionConnection
        )
        self.videoPlayer().durationChanged.disconnect(
            self.__durationConnection 
        )

    def videoSlider(self) -> ClickableSlider:
        """
        Slider to control :meth:`videoPlayer`.
        """
        return self._videoSlider

    @Slot(int)
    def onSliderValueChange(self, position: int):
        """Set the position of media player."""
        self.videoPlayer().setPosition(position)

    @Slot(int)
    def onMediaPositionChange(self, position: int):
        """Change the position of video position slider button."""
        self.videoSlider().setValue(position)

    @Slot(int)
    def onMediaDurationChange(self, duration: int):
        """Change the range of video position slider."""
        self.videoSlider().setRange(0, duration)


class NDArrayVideoPlayerWidget(NDArrayVideoWidget):
    """
    Video player widget with play-pause button and position slider.

    ``QVideoFrame`` from :meth:`mediaPlayer` passes
    :meth:`frameToArrayConverter` and then :meth:`arrayProcessor` to
    be processed, and then displayed on :meth:`videoLabel`.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import get_data_path, NDArrayVideoPlayerWidget
    >>> vidpath = get_data_path('hello.mp4')
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
        player = QMediaPlayer()
        self._videoPlayController = player
        self._mediaPlayer = player
        self._frameToArrayConverter = FrameToArrayConverter()
        self._playButton = QPushButton()
        self._videoSlider = ClickableSlider()
        self._pausedBySliderPress = False
        super().__init__(parent)

        # connect video pipeline
        videoSink = QVideoSink(self)
        self.mediaPlayer().setVideoSink(videoSink)
        videoSink.videoFrameChanged.connect(
            self.frameToArrayConverter().setVideoFrame
        )
        # connect other signals
        self.playButton().clicked.connect(self.onPlayButtonClicked)
        self.videoSlider().sliderPressed.connect(self.onSliderPress)
        self.videoSlider().sliderReleased.connect(self.onSliderRelease)
        self.videoSlider().valueChanged.connect(self.onSliderValueChange)
        self.videoPlayController().playbackStateChanged.connect(
            self.onPlaybackStateChange
        )
        self.mediaPlayer().sourceChanged.connect(self.onMediaSourceChange)
        self.mediaPlayer().positionChanged.connect(self.onMediaPositionChange)
        self.mediaPlayer().durationChanged.connect(self.onMediaDurationChange)

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

    def videoPlayController(self) -> VideoPlayControllerProtocol:
        """
        Worker to accept video playing signal from :meth:`playButton`.

        Note
        ====

        This object does not necessarily produce video stream, but
        controls playback state of video producer.
        """
        return self._videoPlayController

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

    def playButton(self) -> QPushButton:
        return self._playButton

    def videoSlider(self) -> ClickableSlider:
        return self._videoSlider

    def pausedBySliderPress(self) -> bool:
        """If true, video is paused by pressing slider."""
        return self._pausedBySliderPress

    def connectArrayProcessor(self):
        """
        Connect signals to and slots from :meth:`arrayProcessor`.
        """
        super().connectArrayProcessor()
        self.frameToArrayConverter().arrayChanged.connect(
            self.arrayProcessor().setArray
        )

    def disconnectArrayProcessor(self):
        """
        Discoonnect signals to and slots from :meth:`arrayProcessor`.
        """
        super().disconnectArrayProcessor()
        self.frameToArrayConverter().arrayChanged.disconnect(
            self.arrayProcessor().setArray
        )

    @Slot()
    def onPlayButtonClicked(self):
        """Switch play-pause state of media player."""
        if (self.videoPlayController().playbackState()
            == QMediaPlayer.PlayingState):
            self.videoPlayController().pause()
        else:
            self.videoPlayController().play()

    @Slot()
    def onSliderPress(self):
        """Pause if the video was playing."""
        if (self.videoPlayController().playbackState()
            == QMediaPlayer.PlayingState):
            self._pausedBySliderPress = True
            self.videoPlayController().pause()

    @Slot()
    def onSliderRelease(self):
        """Play if the video was paused by :meth:`onSliderPress`."""
        if (self.videoPlayController().playbackState()
            == QMediaPlayer.PausedState):
            if self.pausedBySliderPress():
                self._pausedBySliderPress = False
                self.videoPlayController().play()

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
        self.videoPlayController().stop()
        event.accept()
