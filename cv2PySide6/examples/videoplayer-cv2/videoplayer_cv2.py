"""Video player example using ``cv2.VideoCapture``."""

import cv2
from cv2PySide6 import ArrayProcessor,  NDArrayVideoWidget, CV2VideoPlayer
from numpy.typing import NDArray


class BGRProcessor(ArrayProcessor):
    def processArray(self, array: NDArray) -> NDArray:
        array = super().processArray(array)
        ret = cv2.cvtColor(array, cv2.COLOR_BGR2RGB)
        return ret


class CV2VideoWidget(NDArrayVideoWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._player = CV2VideoPlayer(self)

    def player(self) -> CV2VideoPlayer:
        return self._player

    def closeEvent(self, event):
        self.player().stop()
        super().closeEvent(event)


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    from cv2PySide6 import get_data_path

    app = QApplication(sys.argv)
    processor = BGRProcessor()
    widget = CV2VideoWidget()

    widget.player().arrayChanged.connect(processor.setArray)
    widget.setArrayProcessor(processor)

    widget.player().setSource(get_data_path('hello.mp4'))
    widget.show()
    widget.player().play()
    app.exec()
    app.quit()
