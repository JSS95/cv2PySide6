import cv2
from PySide6.QtGui import QPixmap, Qt
from PySide6.QtMultimedia import QMediaPlayer
from cv2PySide6 import (get_samples_path, NDArrayVideoPlayerWidget,
    ScalableQLabel, array2qimage)


VID_PATH = get_samples_path("hello.mp4")


def test_NDArrayVideoPlayerWidget(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget._video_widget.setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    qtbot.addWidget(vpwidget)

    # open video to videoplayer
    vpwidget.open(VID_PATH)

    # opening the video does not play it
    assert vpwidget._player.playbackState() == QMediaPlayer.StoppedState

    # check preview
    cap = cv2.VideoCapture(VID_PATH)
    _, first_frame = cap.read()
    cap.release()
    ff_bgra = cv2.cvtColor(first_frame, cv2.COLOR_BGR2RGBA)
    first_qimage = QPixmap.fromImage(array2qimage(ff_bgra)).toImage()
    assert vpwidget._video_widget.pixmap().toImage() == first_qimage

    # test that video is played, and stopped when ends
    vpwidget._player.setPlaybackRate(100)
    signals = [
        vpwidget._player.playbackStateChanged,
        vpwidget._player.playbackStateChanged,
        vpwidget._player.mediaStatusChanged,
    ]
    callbacks = [
        lambda state: state == QMediaPlayer.PlayingState,
        lambda state: state == QMediaPlayer.StoppedState,
        lambda status: status == QMediaPlayer.EndOfMedia
    ]
    with qtbot.waitSignals(signals, raising=True, check_params_cbs=callbacks):
        qtbot.mouseClick(vpwidget._play_pause_button, Qt.LeftButton)
    # test last frame is displayed
    assert not vpwidget._video_widget.pixmap().toImage().isNull()

    # XXX: add tests for other features
