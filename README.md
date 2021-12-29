Python package to display video in GUI using `OpenCV-Python` and `PySide6`.

# Introduction

cv2PySide6 is a package which provides utility classes and functions that integrate `cv2` and `PySide6`.

With cv2PySide6, you can build pipeline which reads video with `PySide6`, converts the frame to `numpy` array for processing with `cv2`, and casts it back to `PySide6` object.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless `OpenCV-Python` module modifies the Qt dependency thus making PySide6 unavailable.

`cv2PySide6` can be installed using `pip`.

```
$ pip install cv2PySide6
```

# How to use

1. Subclass `QVideoFrame2Array` to define image processor with custom `processArray` method.
2. Set the video sink of `QMediaPlayer` as frame source of the processor.
3. Set the image processor as array source of `NDArrayVideoWidget`.

In `PySide6`, video frames are acquired as `QVideoFrame` and passed from `QMediaPlayer` to `QVideoSink`, then to `QVideoWidget`.

<div align="center">
  <img src="https://github.com/JSS95/cv2PySide6/raw/master/imgs/pyside6.png"/><br>
    Video display pipeline in PySide6
</div>

In `cv2PySide6`, `QVideoFrame2Array` comes after `QVideoSink`.
This converts the `QVideoFrame` to `numpy.ndarray`, process it, then pass to `NDArrayVideoWidget`.
You can subclass `QVideoFrame2Array` and override `processArray` with your own image processing.

<div align="center">
  <img src="https://github.com/JSS95/cv2PySide6/raw/master/imgs/cv2pyside6.png"/><br>
    Video display pipeline in cv2PySide6
</div>

Use cases are provided in [examples](https://github.com/JSS95/cv2PySide6/tree/master/cv2PySide6/examples) directory.
