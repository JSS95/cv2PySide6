from cv2PySide6 import (
    get_data_path,
    ClickableSlider,
    MediaController,
    NDArrayVideoPlayerWidget,
)
from PySide6.QtCore import Qt, QPoint, QUrl
from PySide6.QtMultimedia import QMediaPlayer


VID_PATH = get_data_path("hello.mp4")


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)
    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)
    assert slider.value() == slider.pixelPosToRangeValue(pos)


def test_MediaController_playpausestop(qtbot):
    controller = MediaController()
    player = QMediaPlayer()
    controller.setPlayer(player)
    player.setLoops(QMediaPlayer.Infinite)
    player.setSource(QUrl.fromLocalFile(VID_PATH))

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == QMediaPlayer.PlayingState,
    ):
        qtbot.mouseClick(controller.playButton(), Qt.LeftButton)

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == QMediaPlayer.PausedState,
    ):
        qtbot.mouseClick(controller.playButton(), Qt.LeftButton)

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == QMediaPlayer.StoppedState,
    ):
        qtbot.mouseClick(controller.stopButton(), Qt.LeftButton)


def test_MediaController_pausedBySliderPress(qtbot):
    controller = MediaController()
    player = QMediaPlayer()
    controller.setPlayer(player)
    player.setLoops(QMediaPlayer.Infinite)
    player.setSource(QUrl.fromLocalFile(VID_PATH))

    qtbot.mousePress(controller.slider(), Qt.LeftButton, pos=QPoint(10, 10))
    assert player.playbackState() == QMediaPlayer.StoppedState
    qtbot.mouseRelease(controller.slider(), Qt.LeftButton)
    assert player.playbackState() == QMediaPlayer.StoppedState

    player.play()
    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == QMediaPlayer.PausedState,
        timeout=None,
    ):
        qtbot.mousePress(controller.slider(), Qt.LeftButton, pos=QPoint(20, 20))

    with qtbot.waitSignal(
        player.playbackStateChanged,
        check_params_cb=lambda state: state == QMediaPlayer.PlayingState,
        timeout=None,
    ):
        qtbot.mouseRelease(controller.slider(), Qt.LeftButton)

    player.pause()
    qtbot.mousePress(controller.slider(), Qt.LeftButton, pos=QPoint(10, 10))
    assert player.playbackState() == QMediaPlayer.PausedState
    qtbot.mouseRelease(controller.slider(), Qt.LeftButton)
    assert player.playbackState() == QMediaPlayer.PausedState


def test_MediaController_slider_range(qtbot):
    controller = MediaController()
    player = QMediaPlayer()
    controller.setPlayer(player)

    with qtbot.waitSignal(controller.slider().rangeChanged):
        player.setSource(QUrl.fromLocalFile(VID_PATH))


def test_NDArrayVideoPlayerWidget(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))
    vpwidget.videoPlayer().setPlaybackRate(100)
    with qtbot.waitSignal(
        vpwidget.videoPlayer().playbackStateChanged,
        check_params_cb=lambda state: state == QMediaPlayer.StoppedState,
        timeout=None,
    ):
        qtbot.mouseClick(vpwidget.videoController().playButton(), Qt.LeftButton)
    assert not vpwidget.videoLabel().pixmap().isNull()
