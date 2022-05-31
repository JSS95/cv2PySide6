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
from .typing import NDArrayMediaCaptureSessionProtocol


__all__ = [
    "ClickableSlider",
    "MediaController",
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
            opt.upsideDown,  # type: ignore[attr-defined]
        )


class MediaController(QWidget):
    """
    Widget to control :class:`QMediaPlayer`.

    This controller can change the playback state and media position by
    :meth:`playButton`, :meth:`stopButton`, and :meth:`slider`.
    Pass :class:`QMediaPlayer` to :meth:`setPlayer` to control it by this widget.

    """

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
        """Slider to change the media position."""
        return self._slider

    def playButton(self) -> QPushButton:
        """Button to play and pause the media."""
        return self._playButton

    def stopButton(self) -> QPushButton:
        """Button to stop the media."""
        return self._stopButton

    def player(self) -> Optional[QMediaPlayer]:
        """Media player which is controlled by *self*."""
        return self._player

    @Slot()
    def onPlayButtonClicked(self):
        """Play or pause :meth:`player`."""
        if self.player() is not None:
            if self.player().playbackState() == QMediaPlayer.PlayingState:
                self.player().pause()
            else:
                self.player().play()

    @Slot()
    def onStopButtonClicked(self):
        """Stop :meth:`player`."""
        if self.player() is not None:
            self.player().stop()

    @Slot()
    def onSliderPress(self):
        """If the media was playing, pause and move to the pressed position."""
        if (
            self.player() is not None
            and self.player().playbackState() == QMediaPlayer.PlayingState
        ):
            self._pausedBySliderPress = True
            self.player().pause()
        self.player().setPosition(self.slider().value())

    @Slot(int)
    def onSliderMove(self, position: int):
        """Move the media to current slider position."""
        player = self.player()
        if player is not None:
            player.setPosition(position)

    @Slot()
    def onSliderRelease(self):
        """If the media was paused by slider press, play the media."""
        if self.player() is not None and self._pausedBySliderPress:
            self.player().play()
            self._pausedBySliderPress = False

    def setPlayer(self, player: Optional[QMediaPlayer]):
        """Set :meth:`player` and connect the signals."""
        old_player = self.player()
        if old_player is not None:
            self.disconnectPlayer(old_player)
        self._player = player
        if player is not None:
            self.connectPlayer(player)

    def connectPlayer(self, player: QMediaPlayer):
        """Connect signals and slots with *player*."""
        player.durationChanged.connect(  # type: ignore[attr-defined]
            self.onMediaDurationChange
        )
        player.playbackStateChanged.connect(  # type: ignore[attr-defined]
            self.onPlaybackStateChange
        )
        player.positionChanged.connect(  # type: ignore[attr-defined]
            self.onMediaPositionChange
        )

    def disconnectPlayer(self, player: QMediaPlayer):
        """Disconnect signals and slots with *player*."""
        player.durationChanged.disconnect(  # type: ignore[attr-defined]
            self.onMediaDurationChange
        )
        player.playbackStateChanged.disconnect(  # type: ignore[attr-defined]
            self.onPlaybackStateChange
        )
        player.positionChanged.disconnect(  # type: ignore[attr-defined]
            self.onMediaPositionChange
        )

    @Slot(int)
    def onMediaDurationChange(self, duration: int):
        """Set the slider range to media duration."""
        self.slider().setRange(0, duration)

    @Slot(QMediaPlayer.PlaybackState)
    def onPlaybackStateChange(self, state: QMediaPlayer.PlaybackState):
        """Switch the play icon and pause icon by *state*."""
        if state == QMediaPlayer.PlayingState:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self.playButton().setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self.playButton().setIcon(play_icon)

    @Slot(int)
    def onMediaPositionChange(self, position: int):
        """Update the slider position to media position."""
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
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._arrayProcessor = ArrayProcessor()
        self._videoLabel = NDArrayLabel()
        self._videoController = MediaController()

        self.videoPlayer().arrayChanged.connect(self.arrayProcessor().setArray)
        self.arrayProcessor().arrayChanged.connect(self.videoLabel().setArray)
        self.videoLabel().setAlignment(Qt.AlignCenter)
        self.videoController().setPlayer(self.videoPlayer())

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        layout.addWidget(self.videoController())
        self.setLayout(layout)

    def videoPlayer(self) -> NDArrayVideoPlayer:
        """Object to emit video frames as numy arrays."""
        return self._videoPlayer

    def arrayProcessor(self) -> ArrayProcessor:
        """Process the array and provide to :meth:`videoLabel`."""
        return self._arrayProcessor

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    def videoController(self) -> MediaController:
        """Widget to control :meth:`videoPlayer`."""
        return self._videoController

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
