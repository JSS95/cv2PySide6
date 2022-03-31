from PySide6.QtCore import QPoint, QUrl
from PySide6.QtGui import Qt

from cv2PySide6 import ClickableSlider, NDArrayVideoPlayer, get_data_path


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)

    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)

    assert slider.value() == slider.pixelPosToRangeValue(pos)


def test_NDArrayMediaPlayer(qtbot):
    player = NDArrayVideoPlayer()
    player.setSource(QUrl.fromLocalFile(get_data_path('hello.mp4')))
    with qtbot.waitSignal(player.arrayChanged):
        player.play()
    player.stop()
