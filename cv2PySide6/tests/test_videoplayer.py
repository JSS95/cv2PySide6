import cv2 # type: ignore
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtMultimedia import QMediaPlayer
from qimage2ndarray import array2qimage # type: ignore

from cv2PySide6 import (get_data_path, NDArrayVideoPlayerWidget,
    ScalableQLabel)


VID_PATH = get_data_path('hello.mp4')


def test_NDArrayVideoPlayerWidget_openfile(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.open(VID_PATH)

    # opening the video does not play it
    assert vpwidget.mediaPlayer().playbackState() == QMediaPlayer.StoppedState


def test_NDArrayVideoPlayerWidget_preview(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.open(VID_PATH)

    cap = cv2.VideoCapture(VID_PATH)
    _, first_frame = cap.read()
    cap.release()
    ff_bgra = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGBA)
    first_qimage = QPixmap.fromImage(array2qimage(ff_bgra)).toImage()
    assert vpwidget.videoLabel().pixmap().toImage() == first_qimage


def test_NDArrayVideoPlayerWidget_playback(qtbot):
    """
    Test button click plays video, and player stops when video ends.
    """
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.open(VID_PATH)

    vpwidget.mediaPlayer().setPlaybackRate(100)
    with qtbot.waitSignals(
        [
        vpwidget.mediaPlayer().playbackStateChanged,
        vpwidget.mediaPlayer().playbackStateChanged,
        vpwidget.mediaPlayer().mediaStatusChanged,
        ],
        check_params_cbs=[
        lambda state: state == QMediaPlayer.PlayingState,
        lambda state: state == QMediaPlayer.StoppedState,
        lambda status: status == QMediaPlayer.EndOfMedia,
        ]
    ):
        qtbot.mouseClick(vpwidget.playButton(), Qt.LeftButton)


def test_NDArrayVideoPlayerWidget_lastframe_displayed(qtbot):
    """Test that last frame remains on the label after video ends."""
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.open(VID_PATH)
    vpwidget.mediaPlayer().setPlaybackRate(100)
    qtbot.mouseClick(vpwidget.playButton(), Qt.LeftButton)
    qtbot.waitUntil(
        lambda: vpwidget.mediaPlayer().playbackState() \
                != QMediaPlayer.PlayingState
    )
    assert not vpwidget.videoLabel().pixmap().toImage().isNull()


# XXX: add tests for other features
