import cv2  # type: ignore
import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from qimage2ndarray import array2qimage  # type: ignore

from cv2PySide6 import ScalableQLabel, NDArrayLabel, get_data_path

IMG_PATH = get_data_path("hello.jpg")


def test_ScalableQLabel(qtbot):
    label = ScalableQLabel()

    img = cv2.cvtColor(cv2.imread(IMG_PATH), cv2.COLOR_BGR2RGBA)
    pixmap = QPixmap.fromImage(array2qimage(img))
    pixmap_image = pixmap.toImage()
    img_h, img_w = pixmap_image.height(), pixmap_image.width()

    label.setPixmapScaleMode(label.PM_NoScale)
    # pixmap size is fixed
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image
    # test downscaling : size fixed to original size
    new_w, new_h = (int(img_w / 2), int(img_h / 2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image
    # test upscaling : size fixed to original size
    new_w, new_h = (2 * img_w, 2 * img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image

    label.setPixmapScaleMode(label.PM_DownScaleOnly)
    # test downscaling
    new_w, new_h = (int(img_w / 2), int(img_h / 2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() < img_w and label.pixmap().height() < img_h
    # test upscaling : maximum size == original size
    new_w, new_h = (2 * img_w, 2 * img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image

    label.setPixmapScaleMode(label.PM_UpScaleOnly)
    # test downscaling : minimum size == original size
    new_w, new_h = (int(img_w / 2), int(img_h / 2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image
    # test upscaling
    new_w, new_h = (2 * img_w, 2 * img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() > img_w and label.pixmap().height() > img_h

    label.setPixmapScaleMode(label.PM_AllScale)
    # test downscaling
    new_w, new_h = (int(img_w / 2), int(img_h / 2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() < img_w and label.pixmap().height() < img_h
    # test upscaling
    new_w, new_h = (2 * img_w, 2 * img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() > img_w and label.pixmap().height() > img_h


def test_NDArrayLabel(qtbot):
    label = NDArrayLabel()

    img = cv2.imread(IMG_PATH)
    h, w = img.shape[:2]

    label.setPixmapScaleMode(label.PM_NoScale)
    # pixmap size is fixed
    label.setArray(img)
    assert label.pixmap().size() == QSize(w, h)
    # test downscaling : size fixed to original size
    new_w, new_h = (int(w / 2), int(h / 2))
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().size() == QSize(w, h)
    # test upscaling : size fixed to original size
    new_w, new_h = (2 * w, 2 * h)
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().size() == QSize(w, h)

    label.setPixmapScaleMode(label.PM_DownScaleOnly)
    # test downscaling
    new_w, new_h = (int(w / 2), int(h / 2))
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().width() < w and label.pixmap().height() < h
    # test upscaling : maximum size == original size
    new_w, new_h = (2 * w, 2 * h)
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().size() == QSize(w, h)

    label.setPixmapScaleMode(label.PM_UpScaleOnly)
    # test downscaling : minimum size == original size
    new_w, new_h = (int(w / 2), int(h / 2))
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().size() == QSize(w, h)
    # test upscaling : maximum size == original size
    new_w, new_h = (2 * w, 2 * h)
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().width() > w and label.pixmap().height() > h

    label.setPixmapScaleMode(label.PM_AllScale)
    # test downscaling
    new_w, new_h = (int(w / 2), int(h / 2))
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().width() < w and label.pixmap().height() < h
    # test upscaling
    new_w, new_h = (2 * w, 2 * h)
    label.resize(new_w, new_h)
    label.setArray(img)
    assert label.pixmap().width() > w and label.pixmap().height() > h


def test_NDArrayLabel_emptyimage(qtbot):
    label = NDArrayLabel()
    assert label.pixmap().isNull()

    empty_array = np.empty((0, 0, 0), dtype=np.uint8)
    label.setArray(empty_array)
    assert label.pixmap().isNull()
