from cv2PySide6 import (
    get_data_path,
    ClickableSlider,
    NDArrayVideoPlayerWidget,
    ScalableQLabel,
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


def test_NDArrayVideoPlayerWidget_openfile(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))

    # opening the video does not play it
    assert vpwidget.videoPlayer().playbackState() == QMediaPlayer.StoppedState
