import cv2 # type: ignore
from PySide6.QtCore import QUrl
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtMultimedia import QMediaPlayer
import pytest
from qimage2ndarray import array2qimage # type: ignore

from cv2PySide6 import get_data_path, NDArrayVideoPlayerWidget, ScalableQLabel

VID_PATH = get_data_path('hello.mp4')


def test_NDArrayVideoPlayerWidget_openfile(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))

    # opening the video does not play it
    assert vpwidget.videoPlayer().playbackState() == QMediaPlayer.StoppedState


@pytest.mark.xfail
def test_NDArrayVideoPlayerWidget_preview(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))

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
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))

    vpwidget.videoPlayer().setPlaybackRate(100)
    with qtbot.waitSignals(
        [
        vpwidget.videoPlayer().playbackStateChanged,
        vpwidget.videoPlayer().playbackStateChanged,
        vpwidget.videoPlayer().mediaStatusChanged,
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
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))
    vpwidget.videoPlayer().setPlaybackRate(100)
    qtbot.mouseClick(vpwidget.playButton(), Qt.LeftButton)
    qtbot.waitUntil(
        lambda: vpwidget.videoPlayer().playbackState() \
                != QMediaPlayer.PlayingState
    )
    assert not vpwidget.videoLabel().pixmap().toImage().isNull()


# XXX: add tests for other features
