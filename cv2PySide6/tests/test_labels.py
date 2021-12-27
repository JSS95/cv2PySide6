import cv2
import numpy as np
from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from cv2PySide6 import (array2qimage, qimage2array,
    ScalableQLabel, NDArrayLabel, get_samples_path)

IMG_PATH = get_samples_path("hello.jpg")


def test_array2qimage():
    img_array = cv2.cvtColor(cv2.imread(IMG_PATH), cv2.COLOR_BGR2RGBA)

    h, w = img_array.shape[:2]

    qimage = array2qimage(img_array)
    assert qimage.width() == w
    assert qimage.height() == h
    assert qimage.bytesPerLine() == w * 4
    assert qimage.sizeInBytes() == img_array.size


def test_qimage2array():
    bgr_img = cv2.imread(IMG_PATH)
    img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGBA)

    qimage = array2qimage(img)
    img2 = qimage2array(qimage)

    assert img.shape == img2.shape
    assert np.all(img == img2)


def test_ScalableQLabel(qtbot):
    label = ScalableQLabel()
    qtbot.addWidget(label)

    img_array = cv2.cvtColor(cv2.imread(IMG_PATH), cv2.COLOR_BGR2RGBA)
    pixmap = QPixmap.fromImage(array2qimage(img_array))
    pixmap_image = pixmap.toImage()
    img_h, img_w = pixmap_image.height(), pixmap_image.width()

    label.setPixmapScaleMode(label.PM_NoScale)
    # pixmap size is fixed
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image
    # test downscaling : size fixed to original size
    new_w, new_h = (int(img_w/2), int(img_h/2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image
    # test upscaling : size fixed to original size
    new_w, new_h = (2*img_w, 2*img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image

    label.setPixmapScaleMode(label.PM_DownScaleOnly)
    # test downscaling
    new_w, new_h = (int(img_w/2), int(img_h/2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() < img_w and label.pixmap().height() < img_h
    # test upscaling : maximum size == original size
    new_w, new_h = (2*img_w, 2*img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image

    label.setPixmapScaleMode(label.PM_UpScaleOnly)
    # test downscaling : minimum size == original size
    new_w, new_h = (int(img_w/2), int(img_h/2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().size() == QSize(img_w, img_h)
    assert label.pixmap().toImage() == pixmap_image
    # test upscaling
    new_w, new_h = (2*img_w, 2*img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() > img_w and label.pixmap().height() > img_h

    label.setPixmapScaleMode(label.PM_AllScale)
    # test downscaling
    new_w, new_h = (int(img_w/2), int(img_h/2))
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() < img_w and label.pixmap().height() < img_h
    # test upscaling
    new_w, new_h = (2*img_w, 2*img_h)
    label.resize(new_w, new_h)
    label.setPixmap(pixmap)
    assert label.pixmap().width() > img_w and label.pixmap().height() > img_h


def test_NDArrayLabel(qtbot):
    # Note : When converting QImage -> QPixmap -> QImage, the resulting
    # QImage may have different channel (i.e. monochrome RGB to binary).
    # Therefore we do not use the original array for comparison.

    label = NDArrayLabel()
    qtbot.addWidget(label)

    img_array = cv2.cvtColor(cv2.imread(IMG_PATH), cv2.COLOR_BGR2RGBA)
    pixmap_image = QPixmap.fromImage(array2qimage(img_array)).toImage()
    pixmap_array = qimage2array(pixmap_image)
    arr_h, arr_w = pixmap_array.shape[:2]

    label.setPixmapScaleMode(label.PM_NoScale)
    # pixmap size is fixed
    label.setArray(img_array)
    assert label.pixmap().size() == QSize(arr_w, arr_h)
    assert np.all(qimage2array(label.pixmap().toImage()) == pixmap_array)
    # test downscaling : size fixed to original size
    new_w, new_h = (int(arr_w/2), int(arr_h/2))
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().size() == QSize(arr_w, arr_h)
    assert np.all(qimage2array(label.pixmap().toImage()) == pixmap_array)
    # test upscaling : size fixed to original size
    new_w, new_h = (2*arr_w, 2*arr_h)
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().size() == QSize(arr_w, arr_h)
    assert np.all(qimage2array(label.pixmap().toImage()) == pixmap_array)

    label.setPixmapScaleMode(label.PM_DownScaleOnly)
    # test downscaling
    new_w, new_h = (int(arr_w/2), int(arr_h/2))
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().width() < arr_w and label.pixmap().height() < arr_h
    # test upscaling : maximum size == original size
    new_w, new_h = (2*arr_w, 2*arr_h)
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().size() == QSize(arr_w, arr_h)
    assert np.all(qimage2array(label.pixmap().toImage()) == pixmap_array)

    label.setPixmapScaleMode(label.PM_UpScaleOnly)
    # test downscaling : minimum size == original size
    new_w, new_h = (int(arr_w/2), int(arr_h/2))
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().size() == QSize(arr_w, arr_h)
    assert np.all(qimage2array(label.pixmap().toImage()) == pixmap_array)
    # test upscaling : maximum size == original size
    new_w, new_h = (2*arr_w, 2*arr_h)
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().width() > arr_w and label.pixmap().height() > arr_h

    label.setPixmapScaleMode(label.PM_AllScale)
    # test downscaling
    new_w, new_h = (int(arr_w/2), int(arr_h/2))
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().width() < arr_w and label.pixmap().height() < arr_h
    # test upscaling
    new_w, new_h = (2*arr_w, 2*arr_h)
    label.resize(new_w, new_h)
    label.setArray(img_array)
    assert label.pixmap().width() > arr_w and label.pixmap().height() > arr_h
