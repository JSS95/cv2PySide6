"""
Video widgets
=============

:mod:`cv2PySide6.videowidgets` provides convenience widgets with pre-built
video pipelines.

"""

import numpy as np
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QWidget, QVBoxLayout
from .labels import NDArrayLabel
from .videostream import NDArrayVideoPlayer, NDArrayMediaCaptureSession
from .videoutil import MediaController


__all__ = [
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
]


class NDArrayVideoPlayerWidget(QWidget):
    """
    Convenience widget to process and display numpy arrays from local video file.

    Examples
    ========

    >>> from PySide6.QtCore import QUrl
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import get_data_path, NDArrayVideoPlayerWidget
    >>> vidpath = get_data_path('hello.mp4')
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     w = NDArrayVideoPlayerWidget()
    ...     w.videoPlayer().setSource(QUrl.fromLocalFile(vidpath))
    ...     w.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    Notes
    =====

    This widget processes the frames with single thread, therefore long
    processing blocks the GUI. Refer to the package examples for building
    multithread pipeline.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._videoPlayer = NDArrayVideoPlayer(self)
        self._videoLabel = NDArrayLabel()
        self._mediaController = MediaController()

        self.videoPlayer().arrayChanged.connect(self.setArray)
        self.videoLabel().setAlignment(Qt.AlignCenter)
        self.mediaController().setPlayer(self.videoPlayer())

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        layout.addWidget(self.mediaController())
        self.setLayout(layout)

    def videoPlayer(self) -> NDArrayVideoPlayer:
        """Object to emit video frames as numpy arrays."""
        return self._videoPlayer

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    def mediaController(self) -> MediaController:
        """Widget to control :meth:`videoPlayer`."""
        return self._mediaController

    @Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        """
        Process the array with :meth:`processArray` and set to :meth:`videoLabel`.
        """
        ret = self.processArray(array)
        self.videoLabel().setArray(ret)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """Perform array processing. Redefine this method if needed."""
        return array


class NDArrayCameraWidget(QWidget):
    """
    Convenience widget to process and display numpy arrays from camera.

    Examples
    ========

    >>> from PySide6.QtWidgets import QApplication
    >>> from PySide6.QtMultimedia import QCamera
    >>> import sys
    >>> from cv2PySide6 import NDArrayCameraWidget
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     widget = NDArrayCameraWidget()
    ...     camera = QCamera()
    ...     widget.mediaCaptureSession().setCamera(camera)
    ...     camera.start()
    ...     widget.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    Notes
    =====

    This widget processes the frames with single thread, therefore long
    processing blocks the GUI. Refer to the package examples for building
    multithread pipeline.

    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self._mediaCaptureSession = NDArrayMediaCaptureSession()
        self._videoLabel = NDArrayLabel()

        self.mediaCaptureSession().arrayChanged.connect(self.setArray)
        self.videoLabel().setAlignment(Qt.AlignCenter)

        layout = QVBoxLayout()
        layout.addWidget(self.videoLabel())
        self.setLayout(layout)

    def mediaCaptureSession(self) -> NDArrayMediaCaptureSession:
        return self._mediaCaptureSession

    def videoLabel(self) -> NDArrayLabel:
        """Label to display video image."""
        return self._videoLabel

    @Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        """
        Process the array with :meth:`processArray` and set to :meth:`videoLabel`.
        """
        ret = self.processArray(array)
        self.videoLabel().setArray(ret)

    def processArray(self, array: np.ndarray) -> np.ndarray:
        """Perform array processing. Redefine this method if needed."""
        return array
