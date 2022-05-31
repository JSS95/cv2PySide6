"""
Widgets to play video stream.
"""

import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, QPointF, Slot
from PySide6.QtGui import QMouseEvent, QCloseEvent
from PySide6.QtWidgets import (
    QSlider,
    QStyleOptionSlider,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QStyle,
    QPushButton,
)
from PySide6.QtMultimedia import QMediaPlayer
from typing import Optional
from .labels import NDArrayLabel
from .videostream import ArrayProcessor, NDArrayVideoPlayer, NDArrayMediaCaptureSession
from .typing import NDArrayVideoPlayerProtocol, NDArrayMediaCaptureSessionProtocol


__all__ = [
    "ClickableSlider",
    "VideoController",
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
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
            opt.upsideDown,
        )


class VideoController(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._slider = ClickableSlider()
        self._playButton = QPushButton()
        self._stopButton = QPushButton()
        self._player = None
        self._pausedBySliderPress = False

        self.playButton().clicked.connect(self.onPlayButtonClicked)
        self.stopButton().clicked.connect(self.onStopButtonClicked)
        self.slider().sliderPressed.connect(self.onSliderPress)
        self.slider().sliderMoved.connect(self.onSliderMove)
        self.slider().sliderReleased.connect(self.onSliderRelease)

        layout = QHBoxLayout()
        play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.playButton().setIcon(play_icon)
        layout.addWidget(self.playButton())
        stop_icon = self.style().standardIcon(QStyle.SP_MediaStop)
        self.stopButton().setIcon(stop_icon)
        layout.addWidget(self.stopButton())
        self.slider().setOrientation(Qt.Horizontal)
        layout.addWidget(self.slider())
        self.setLayout(layout)

    def slider(self) -> ClickableSlider:
        return self._slider

    def playButton(self) -> QPushButton:
        return self._playButton

    def stopButton(self) -> QPushButton:
        return self._stopButton

    def player(self) -> Optional[QMediaPlayer]:
        return self._player

    @Slot()
    def onPlayButtonClicked(self):
        if self.player() is not None:
            if self.player().playbackState() == QMediaPlayer.PlayingState:
                self.player().pause()
            else:
                self.player().play()

    @Slot()
    def onStopButtonClicked(self):
        if self.player() is not None:
            self.player().stop()

    @Slot()
    def onSliderPress(self):
        if (
            self.player() is not None
            and self.player().playbackState() == QMediaPlayer.PlayingState
        ):
            self._pausedBySliderPress = True
            self.player().pause()
            self.player().setPosition(self.slider().value())

    @Slot(int)
    def onSliderMove(self, position: int):
        player = self.player()
        if player is not None:
            player.setPosition(position)

    @Slot()
    def onSliderRelease(self):
        if self.player() is not None and self._pausedBySliderPress:
            self.player().play()
            self._pausedBySliderPress = False

    def setPlayer(self, player: Optional[QMediaPlayer]):
        old_player = self.player()
        if old_player is not None:
            self.disconnectPlayer(old_player)
        self._player = player
        if player is not None:
            self.connectPlayer(player)

    def connectPlayer(self, player: QMediaPlayer):
        player.durationChanged.connect(self.onMediaDurationChange)
        player.playbackStateChanged.connect(self.onPlaybackStateChange)
        player.positionChanged.connect(self.onMediaPositionChange)

    def disconnectPlayer(self, player: QMediaPlayer):
        player.durationChanged.disconnect(self.onMediaDurationChange)
        player.playbackStateChanged.disconnect(self.onPlaybackStateChange)
        player.positionChanged.disconnect(self.onMediaPositionChange)

    @Slot(int)
    def onMediaDurationChange(self, duration: int):
        self.slider().setRange(0, duration)

    @Slot(QMediaPlayer.PlaybackState)
    def onPlaybackStateChange(self, state: QMediaPlayer.PlaybackState):
        if state == QMediaPlayer.PlayingState:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self.playButton().setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self.playButton().setIcon(play_icon)

    @Slot(int)
    def onMediaPositionChange(self, position: int):
        self.slider().setValue(position)


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
        """Object to emit video frames as numy arrays."""
        return self._videoPlayer

    def setVideoPlayer(self, player: NDArrayVideoPlayerProtocol):
        """
        Update :meth:`videoPlayer` with *player* and reconnect signals.

        Notes
        =====

        *player* must have *self* as parent before being passed to this
        method, in order to prevent undesired destruction.

        """
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
        self.videoPlayer().arrayChanged.disconnect(self._processConnection)
        self.videoPlayer().positionChanged.disconnect(self._positionConnection)
        self.videoPlayer().durationChanged.disconnect(self._durationConnection)
        self.videoPlayer().playbackStateChanged.disconnect(self._playConnect)

    def arrayProcessor(self) -> ArrayProcessor:
        """Process the array and provide to :meth:`videoLabel`."""
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
        self.__displayConnection = self.arrayProcessor().arrayChanged.connect(
            self.videoLabel().setArray
        )

    def disconnectArrayProcessor(self):
        """
        Discoonnect signals to and slots from :meth:`arrayProcessor`.
        """
        self.arrayProcessor().arrayChanged.disconnect(self.__displayConnection)

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    def videoSlider(self) -> ClickableSlider:
        """Slider to control :meth:`videoPlayer`."""
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
        if self.videoPlayer().playbackState() != QMediaPlayer.PlayingState:
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
        if self.videoPlayer().playbackState() == QMediaPlayer.PlayingState:
            self.videoPlayer().pause()
        else:
            self.videoPlayer().play()

    @Slot()
    def onStopButtonClicked(self):
        self.videoPlayer().stop()

    @Slot()
    def onSliderPress(self):
        """Pause if the video was playing."""
        if self.videoPlayer().playbackState() == QMediaPlayer.PlayingState:
            self._pausedBySliderPress = True
            self.videoPlayer().pause()
            self.onSliderValueChange(self.videoSlider().value())

    @Slot()
    def onSliderRelease(self):
        """Play if the video was paused by :meth:`onSliderPress`."""
        if self.videoPlayer().playbackState() == QMediaPlayer.PausedState:
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
        self.mediaCaptureSession().arrayChanged.disconnect(self.__processConnection)

    def arrayProcessor(self) -> ArrayProcessor:
        """Process the array and provide to :meth:`videoLabel`."""
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
        self.__displayConnection = self.arrayProcessor().arrayChanged.connect(
            self.videoLabel().setArray
        )

    def disconnectArrayProcessor(self):
        """
        Discoonnect signals to and slots from :meth:`arrayProcessor`.
        """
        self.arrayProcessor().arrayChanged.disconnect(self.__displayConnection)

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    @Slot(np.ndarray)
    def onArrayPassedFromCamera(self, array: NDArray):
        self.arrayProcessor().setArray(array)
