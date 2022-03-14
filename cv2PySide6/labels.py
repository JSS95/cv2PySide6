import enum
import numpy as np
from numpy.typing import NDArray
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QLabel, QSizePolicy

from qimage2ndarray import array2qimage

__all__ = [
    "ScalableQLabel",
    "NDArrayLabel",
    "qimage2array",
]


class ScalableQLabel(QLabel):
    """
    A label which can scale the pixmap before displaying.

    To enable scaling while updating (e.g. displaying a playing video),
    two things are done.

    1. ``sizePolicy()`` is set to ``QSizePolicy.Expanding`` in x and y.
       Other policies are not tested.

    2. ``minimumSize()`` is set to ``(1, 1)``. Note that ``(0, 0)`` will
       prevent free resizing.

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

        self._pixmapScaleMode = self.PM_DownScaleOnly
        empty_qimg = QImage(0, 0, QImage.Format_RGB888)
        self._original_pixmap = QPixmap.fromImage(empty_qimg)

        # make label shrinkable
        self.setSizePolicy(QSizePolicy.Expanding,
                           QSizePolicy.Expanding)
        self.setMinimumSize(1, 1)

    def pixmapScaleMode(self) -> PixmapScaleMode:
        """
        Mode to scale the ``QPixmap`` by :meth:`scalePixmap`.
        Default is :attr:`PM_DownScaleOnly`.

        """
        return self._pixmapScaleMode

    def setPixmapScaleMode(self, flag: PixmapScaleMode):
        self._pixmapScaleMode = flag

    def scalePixmap(self, pixmap: QPixmap) -> QPixmap:
        """
        Scale the pixmap with respect to the size of self.

        See Also
        ========

        PixmapScaleMode

        """
        scalemod = self.pixmapScaleMode()
        if scalemod == self.PM_NoScale:
            flag = False
        else:
            w, h = pixmap.width(), pixmap.height()
            new_w = self.width()
            new_h = self.height()
            if scalemod == self.PM_DownScaleOnly:
                flag = new_w < w or new_h < h
            elif scalemod == self.PM_UpScaleOnly:
                flag = new_w > w or new_h > h
            elif scalemod == self.PM_AllScale:
                flag = True
            else:
                msg = "Unrecognized pixmap scale mode: %s" % scalemod
                raise TypeError(msg)

        if flag:
            pixmap = pixmap.scaled(new_w, new_h, Qt.KeepAspectRatio)

        return pixmap

    @Slot(QPixmap)
    def setPixmap(self, pixmap: QPixmap):
        """
        Scale the pixmap and display.

        See Also
        ========

        scalePixmap

        """
        self._original_pixmap = pixmap
        scaled_pixmap = self.scalePixmap(pixmap)
        super().setPixmap(scaled_pixmap)

    def paintEvent(self, event):
        """Resets the current pixmap size when resizing the widget"""
        super().paintEvent(event)
        self.setPixmap(self._original_pixmap)


class NDArrayLabel(ScalableQLabel):
    """
    A scalable label which can receive and display
    :class:`numpy.ndarray` image.

    Examples
    ========

    >>> import cv2
    >>> from PySide6.QtWidgets import QApplication
    >>> import sys
    >>> from cv2PySide6 import NDArrayLabel, get_data_path
    >>> img = cv2.imread(get_data_path("hello.jpg"))
    >>> img_rgba = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
    >>> def runGUI():
    ...     app = QApplication(sys.argv)
    ...     label = NDArrayLabel()
    ...     geometry = label.screen().availableGeometry()
    ...     label.resize(geometry.width() / 3, geometry.height() / 2)
    ...     label.setArray(img_rgba)
    ...     label.show()
    ...     app.exec()
    ...     app.quit()
    >>> runGUI() # doctest: +SKIP

    """
    @Slot(np.ndarray)
    def setArray(self, array: NDArray):
        """
        Convert the RGBA array to ``QPixmap`` and display.

        """
        pixmap = QPixmap.fromImage(array2qimage(array))
        self.setPixmap(pixmap)


def qimage2array(qimg: QImage) -> NDArray:
    """
    Convert the ``QImage`` to :class:`numpy.ndarray`.

    The resulting array does not share the memory with *qimg*.
    """
    w = qimg.width()
    h = qimg.height()
    ch = int(qimg.sizeInBytes()/w/h)

    ptr = qimg.constBits()
    array = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, ch)).copy()
    return array
