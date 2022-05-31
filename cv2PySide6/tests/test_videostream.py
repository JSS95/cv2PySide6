import cv2  # type: ignore
import numpy as np
from PySide6.QtCore import QPoint, QUrl
from PySide6.QtGui import Qt
import pytest
from qimage2ndarray import byte_view, gray2qimage, array2qimage  # type: ignore

from cv2PySide6 import (
    FrameToArrayConverter,
    ClickableSlider,
    NDArrayVideoPlayer,
    get_data_path,
)


def test_FrameToArrayConverter(qtbot):
    bgr_array = cv2.imread(get_data_path("hello.jpg"))
    gray_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2GRAY)
    rgb_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2RGB)
    gray_img = gray2qimage(gray_array)
    rgb_img = array2qimage(rgb_array)

    conv = FrameToArrayConverter()
    assert np.all(conv.convertQImageToArray(rgb_img) == rgb_array)
    with pytest.raises(ValueError):
        conv.convertQImageToArray(gray_img)

    conv.setConverter(byte_view)
    assert np.all(conv.convertQImageToArray(gray_img) == gray_array[..., np.newaxis])


def test_ClickableSlider(qtbot):
    slider = ClickableSlider()
    qtbot.addWidget(slider)

    assert slider.value() == 0

    pos = QPoint(10, 10)
    qtbot.mouseClick(slider, Qt.LeftButton, pos=pos)

    assert slider.value() == slider.pixelPosToRangeValue(pos)


def test_NDArrayVideoPlayer(qtbot):
    player = NDArrayVideoPlayer()
    player.setSource(QUrl.fromLocalFile(get_data_path("hello.mp4")))
    with qtbot.waitSignal(player.arrayChanged):
        player.play()
    player.stop()
