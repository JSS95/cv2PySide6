from cv2PySide6 import get_data_path, ClickableSlider
from PySide6.QtCore import Qt, QPoint


VID_PATH = get_data_path("hello.mp4")


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)
    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)
    assert slider.value() == slider.pixelPosToRangeValue(pos)
