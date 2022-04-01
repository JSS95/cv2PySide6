"""
Widgets to play video stream.
"""

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QCloseEvent
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QStyle,
    QPushButton)
from PySide6.QtMultimedia import QMediaPlayer

from .labels import NDArrayLabel
from .videoutil import (ClickableSlider, ArrayProcessor, NDArrayVideoPlayer,
    NDArrayMediaCaptureSession)
from .typing import (ArrayProcessorProtocol, NDArrayVideoPlayerProtocol,
    NDArrayMediaCaptureSessionProtocol)


__all__ = [
    'NDArrayVideoPlayerWidget',
    'NDArrayCameraWidget',
]


class NDArrayVideoPlayerWidget(QWidget):
    """
    Widget to display numpy arrays from local video file.

    Examples
    ========

    >>> from PySide6.QtCore import QUrl
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import get_data_path, NDArrayVideoPlayerWidget
    >>> vidpath = get_data_path('hello.mp4')
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     w = NDArrayVideoPlayerWidget()
    ...     w.videoPlayer().setSource(QUrl.fromLocalFile(vidpath))
    ...     w.show()
    ...     w.videoPlayer().play()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._arrayProcessor = ArrayProcessor()
        self._videoLabel = NDArrayLabel()
        self._videoSlider = ClickableSlider()
        self._playButton = QPushButton()
        self._stopButton = QPushButton()
        self._pausedBySliderPress = False

        self.connectVideoPlayer()
        self.connectArrayProcessor()
        self.videoLabel().setAlignment(Qt.AlignCenter)
        self.playButton().clicked.connect(self.onPlayButtonClicked)
        self.stopButton().clicked.connect(self.onStopButtonClicked)
        self.videoSlider().valueChanged.connect(self.onSliderValueChange)
        self.videoSlider().sliderPressed.connect(self.onSliderPress)
        self.videoSlider().sliderReleased.connect(self.onSliderRelease)

        self.initUI()

    def initUI(self):
        control_layout = QHBoxLayout()
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.playButton().setIcon(play_icon)
        control_layout.addWidget(self.playButton())
        stop_icon = self.style().standardIcon(QStyle.SP_MediaStop)
        self.stopButton().setIcon(stop_icon)
        control_layout.addWidget(self.stopButton())
        self.videoSlider().setOrientation(Qt.Horizontal)
        control_layout.addWidget(self.videoSlider())

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        layout.addLayout(control_layout)
        self.setLayout(layout)

    def videoPlayer(self) -> NDArrayVideoPlayerProtocol:
        return self._videoPlayer

    def setVideoPlayer(self, player: NDArrayVideoPlayerProtocol):
        self.disconnectVideoPlayer()
        self._videoPlayer = player
        self.connectVideoPlayer()

    def connectVideoPlayer(self):
        self._processConnection = self.videoPlayer().arrayChanged.connect(
            self.onArrayPassedFromPlayer
        )
        self._positionConnection = self.videoPlayer().positionChanged.connect(
            self.onMediaPositionChange
        )
        self._durationConnection = self.videoPlayer().durationChanged.connect(
            self.onMediaDurationChange
        )
        self._playConnect = self.videoPlayer().playbackStateChanged.connect(
            self.onPlaybackStateChange
        )

    def disconnectVideoPlayer(self):
        self.videoPlayer().arrayChanged.disconnect(
            self._processConnection
        )
        self.videoPlayer().positionChanged.disconnect(
            self._positionConnection
        )
        self.videoPlayer().durationChanged.disconnect(
            self._durationConnection 
        )
        self.videoPlayer().playbackStateChanged.disconnect(
            self._playConnect
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

    def videoSlider(self) -> ClickableSlider:
        """
        Slider to control :meth:`videoPlayer`.
        """
        return self._videoSlider

    def playButton(self) -> QPushButton:
        return self._playButton

    def stopButton(self) -> QPushButton:
        return self._stopButton

    def pausedBySliderPress(self) -> bool:
        """If true, video is paused by pressing slider."""
        return self._pausedBySliderPress

    @Slot(np.ndarray)
    def onArrayPassedFromPlayer(self, array: NDArray):
        self.arrayProcessor().setArray(array)

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

    @Slot()
    def onPlayButtonClicked(self):
        """Switch play-pause state of media player."""
        if (self.videoPlayer().playbackState()
            == QMediaPlayer.PlayingState):
            self.videoPlayer().pause()
        else:
            self.videoPlayer().play()

    @Slot()
    def onStopButtonClicked(self):
        self.videoPlayer().stop()

    @Slot()
    def onSliderPress(self):
        """Pause if the video was playing."""
        if (self.videoPlayer().playbackState()
            == QMediaPlayer.PlayingState):
            self._pausedBySliderPress = True
            self.videoPlayer().pause()

    @Slot()
    def onSliderRelease(self):
        """Play if the video was paused by :meth:`onSliderPress`."""
        if (self.videoPlayer().playbackState()
            == QMediaPlayer.PausedState):
            if self.pausedBySliderPress():
                self._pausedBySliderPress = False
                self.videoPlayer().play()

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
        """Stop :meth:`mediaPlayer` before closing."""
        self.videoPlayer().stop()
        event.accept()


class NDArrayCameraWidget(QWidget):
    """
    Widget to display numpy arrays from camera.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> from PySide6.QtMultimedia import QMediaDevices, QCamera
    >>> import sys
    >>> from cv2PySide6 import NDArrayCameraWidget
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     widget = NDArrayCameraWidget()
    ...     cameras = QMediaDevices.videoInputs()
    ...     if cameras:
    ...         camera = QCamera(cameras[0])
    ...         widget.mediaCaptureSession().setCamera(camera)
    ...         camera.start()
    ...     widget.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    """
    def __init__(self, parent=None):
        super().__init__(parent)

        self._mediaCaptureSession = NDArrayMediaCaptureSession()
        self._arrayProcessor = ArrayProcessor()
        self._videoLabel = NDArrayLabel()

        self.connectMediaCaptureSession()
        self.connectArrayProcessor()
        self.videoLabel().setAlignment(Qt.AlignCenter)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        self.setLayout(layout)

    def mediaCaptureSession(self) -> NDArrayMediaCaptureSessionProtocol:
        return self._mediaCaptureSession

    def setMediaCaptureSession(self, sess: NDArrayMediaCaptureSessionProtocol):
        self.disconnectMediaCaptureSession()
        self._mediaCaptureSession = sess
        self.connectMediaCaptureSession()

    def connectMediaCaptureSession(self):
        session = self.mediaCaptureSession()
        self.__processConnection = session.arrayChanged.connect(
            self.onArrayPassedFromCamera
        )

    def disconnectMediaCaptureSession(self):
        self.mediaCaptureSession().arrayChanged.disconnect(
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
    def onArrayPassedFromCamera(self, array: NDArray):
        self.arrayProcessor().setArray(array)
