"""
Utilities to run video.
"""
from PySide6.QtCore import Qt, QPointF, Slot
from PySide6.QtGui import QMouseEvent
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtWidgets import (
    QSlider,
    QStyleOptionSlider,
    QWidget,
    QHBoxLayout,
    QStyle,
    QPushButton,
)
from typing import Optional


__all__ = [
    "ClickableSlider",
    "MediaController",
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
        player.positionChanged.connect(  # type: ignore[attr-defined]
            self.onMediaPositionChange
        )
        player.playbackStateChanged.connect(  # type: ignore[attr-defined]
            self.onPlaybackStateChange
        )

    def disconnectPlayer(self, player: QMediaPlayer):
        """Disconnect signals and slots with *player*."""
        player.durationChanged.disconnect(  # type: ignore[attr-defined]
            self.onMediaDurationChange
        )
        player.positionChanged.disconnect(  # type: ignore[attr-defined]
            self.onMediaPositionChange
        )
        player.playbackStateChanged.disconnect(  # type: ignore[attr-defined]
            self.onPlaybackStateChange
        )

    @Slot(int)
    def onMediaDurationChange(self, duration: int):
        """Set the slider range to media duration."""
        self.slider().setRange(0, duration)

    @Slot(int)
    def onMediaPositionChange(self, position: int):
        """Update the slider position to video position."""
        self.slider().setValue(position)

    @Slot(QMediaPlayer.PlaybackState)
    def onPlaybackStateChange(self, state: QMediaPlayer.PlaybackState):
        """Switch the play icon and pause icon by *state*."""
        if state == QMediaPlayer.PlayingState:
            pause_icon = self.style().standardIcon(QStyle.SP_MediaPause)
            self.playButton().setIcon(pause_icon)
        else:
            play_icon = self.style().standardIcon(QStyle.SP_MediaPlay)
            self.playButton().setIcon(play_icon)
