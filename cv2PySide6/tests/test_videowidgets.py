from cv2PySide6 import (
    get_data_path,
    ClickableSlider,
    VideoController,
    NDArrayVideoPlayer,
    NDArrayVideoPlayerWidget,
)
from PySide6.QtCore import Qt, QPoint, QUrl


VID_PATH = get_data_path("hello.mp4")


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)
    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)
    assert slider.value() == slider.pixelPosToRangeValue(pos)


def test_VideoController_playpausestop(qtbot):
    controller = VideoController()
    player = NDArrayVideoPlayer()
    controller.setPlayer(player)
    player.setLoops(NDArrayVideoPlayer.Infinite)
    player.setSource(QUrl.fromLocalFile(VID_PATH))

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == NDArrayVideoPlayer.PlayingState,
    ):
        qtbot.mouseClick(controller.playButton(), Qt.LeftButton)

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == NDArrayVideoPlayer.PausedState,
    ):
        qtbot.mouseClick(controller.playButton(), Qt.LeftButton)

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == NDArrayVideoPlayer.StoppedState,
    ):
        qtbot.mouseClick(controller.stopButton(), Qt.LeftButton)


def test_VideoController_slider_range(qtbot):
    controller = VideoController()
    player = NDArrayVideoPlayer()
    controller.setPlayer(player)

    with qtbot.waitSignal(controller.slider().rangeChanged):
        player.setSource(QUrl.fromLocalFile(VID_PATH))


def test_NDArrayVideoPlayerWidget(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))
    vpwidget.videoPlayer().setPlaybackRate(100)
    with qtbot.waitSignal(
        vpwidget.videoPlayer().playbackStateChanged,
        check_params_cb=lambda state: state == NDArrayVideoPlayer.StoppedState,
        timeout=None,
    ):
        qtbot.mouseClick(vpwidget.videoController().playButton(), Qt.LeftButton)
    assert not vpwidget.videoLabel().pixmap().isNull()
