from cv2PySide6 import get_data_path, NDArrayVideoPlayerWidget, ScalableQLabel
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer


VID_PATH = get_data_path("hello.mp4")


def test_NDArrayVideoPlayerWidget_openfile(qtbot):
    vpwidget = NDArrayVideoPlayerWidget()
    vpwidget.videoLabel().setPixmapScaleMode(ScalableQLabel.PM_NoScale)
    vpwidget.videoPlayer().setSource(QUrl.fromLocalFile(VID_PATH))

    # opening the video does not play it
    assert vpwidget.videoPlayer().playbackState() == QMediaPlayer.StoppedState
