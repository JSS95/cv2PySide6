"""
cv2PySide6
==========

Package to display video in GUI using OpenCV-Python and PySide6 by converting
``QVideoFrame`` to :class:`numpy.ndarray`, process, and convert back to
``QImage``.

This package provides

1. Object to convert ``QVideoFrame`` to :class:`numpy.ndarray`.
2. Widget to directly display :class:`numpy.ndarray`.
3. Convenience objects and widgets to run the video with single thread.
4. Utility widget to control the video.

"""

from .version import __version__  # noqa

from .labels import ScalableQLabel, NDArrayLabel
from .videostream import (
    FrameToArrayConverter,
    NDArrayVideoPlayer,
    NDArrayMediaCaptureSession,
)
from .videowidgets import (
    ClickableSlider,
    MediaController,
    NDArrayVideoPlayerWidget,
    NDArrayCameraWidget,
)
from .util import get_data_path


__all__ = [
    "ScalableQLabel",
    "NDArrayLabel",
    "FrameToArrayConverter",
    "ClickableSlider",
    "MediaController",
    "NDArrayVideoPlayer",
    "NDArrayMediaCaptureSession",
    "NDArrayVideoPlayerWidget",
    "NDArrayCameraWidget",
    "get_data_path",
]
