import enum
import numpy as np
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QSizePolicy

from qimage2ndarray import array2qimage # type: ignore

__all__ = [
    'ScalableQLabel',
    'NDArrayLabel',
]


class ScalableQLabel(QLabel):
    """
    A label which can scale the pixmap before displaying.

    Pixmap can be downscaled or upscaled to fit to the label size,
    depending on :meth:`pixmapScaleMode` value. Scaling mode can be
    set by :meth:`setPixmapScaleMode`.

    :meth:`setPixmap` scales the input pixmap and update to label.
    :meth:`originalPixmap` returns current unscaled pixmap.

    Notes
    =====

    Do not modify the size policy and minimum size value. Changing them
    makes the label not shrinkable.

    """

    class PixmapScaleMode(enum.Enum):
        """
        This enum defines how the pixmap is scaled before being
        displayed.

        Attributes
        ==========

        PM_NoScale
            Pixmap is never scaled. If the label size is smaller than
            the pixmap size, only a part of the pixmap is displayed.

        PM_DownScaleOnly
            Pixmap is scaled, but never larger than its original size.

        PM_UpScaleOnly
            Pixmap is scaled, but never smaller than its original size.

        PM_AllScale
            Pixmap is scaled to any size.

        """
        PM_NoScale = 0
        PM_DownScaleOnly = 1
        PM_UpScaleOnly = 2
        PM_AllScale = 3

    PM_NoScale = PixmapScaleMode.PM_NoScale
    PM_DownScaleOnly = PixmapScaleMode.PM_DownScaleOnly
    PM_UpScaleOnly = PixmapScaleMode.PM_UpScaleOnly
    PM_AllScale = PixmapScaleMode.PM_AllScale

    def __init__(self, parent=None):
        super().__init__(parent)

        self._original_pixmap = QPixmap()
        self._pixmapScaleMode = self.PM_DownScaleOnly
        # make label shrinkable
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)
        self.setMinimumSize(1, 1) # (0, 0) prevents resizing

    def originalPixmap(self) -> QPixmap:
        """Original pixmap before scaling."""
        return self._original_pixmap

    def pixmapScaleMode(self) -> PixmapScaleMode:
        """
        Mode to scale the pixmap. Default is :attr:`PM_DownScaleOnly`.
        """
        return self._pixmapScaleMode

    @Slot(PixmapScaleMode)
    def setPixmapScaleMode(self, flag: PixmapScaleMode):
        """Set :meth:`pixmapScaleMode` to *flag* and update self."""
        self._pixmapScaleMode = flag
        self.update()

    @Slot(QPixmap)
    def setPixmap(self, pixmap: QPixmap):
        """Scale the pixmap and display."""
        self._original_pixmap = pixmap

        mode = self.pixmapScaleMode()
        if mode == self.PM_NoScale:
            flag = False
        else:
            w, h = pixmap.width(), pixmap.height()
            new_w = self.width()
            new_h = self.height()
            if mode == self.PM_DownScaleOnly:
                flag = new_w < w or new_h < h
            elif mode == self.PM_UpScaleOnly:
                flag = new_w > w or new_h > h
            elif mode == self.PM_AllScale:
                flag = True
            else:
                msg = 'Unrecognized pixmap scale mode: %s' % mode
                raise TypeError(msg)

        if flag:
            pixmap = pixmap.scaled(new_w, new_h, Qt.KeepAspectRatio)

        super().setPixmap(pixmap)

    def paintEvent(self, event):
        super().paintEvent(event)
        self.setPixmap(self.originalPixmap())


class NDArrayLabel(ScalableQLabel):
    """
    Scalable label which can receive and display :class:`numpy.ndarray`
    image. Image array can be set by :meth:`setArray`.

    Examples
    ========

    >>> import cv2
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import NDArrayLabel, get_data_path
    >>> img = cv2.imread(get_data_path("hello.jpg"))
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     label = NDArrayLabel()
    ...     label.setArray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    ...     label.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    """
    @Slot(np.ndarray)
    def setArray(self, array: np.ndarray):
        """Convert the RGB(A) array to pixmap and display."""
        if array.size > 0:
            pixmap = QPixmap.fromImage(array2qimage(array))
        else:
            pixmap = QPixmap()
        self.setPixmap(pixmap)
