import cv2 # type: ignore
from PySide6.QtCore import QPoint
from PySide6.QtGui import Qt

from cv2PySide6 import get_data_path, ClickableSlider, CV2VideoPlayer

VID_PATH = get_data_path('hello.mp4')


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)

    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)

    assert slider.value() == slider.pixelPosToRangeValue(pos)


def test_CV2VideoPlayer_setSource(qtbot):
    player = CV2VideoPlayer()
    assert player.videoCapture() is None
    assert player.duration() == 0
    assert player.position() == 0

    vidcap = cv2.VideoCapture(VID_PATH)
    with qtbot.waitSignals(
        [
            player.sourceChanged,
            player.durationChanged,
            player.positionChanged
        ],
        check_params_cbs=[
            lambda path: path == VID_PATH,
            lambda dur: dur == vidcap.get(cv2.CAP_PROP_FRAME_COUNT),
            lambda pos: pos == 0
        ]
    ):
        player.setSource(VID_PATH)
    assert isinstance(player.videoCapture(), cv2.VideoCapture)
    assert player.duration() == vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    assert player.position() == 0
    vidcap.release()
