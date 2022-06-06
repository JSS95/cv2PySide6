Python package which combines [OpenCV-Python](https://pypi.org/project/opencv-python/) and [PySide6](https://pypi.org/project/PySide6/).

> :warning: This package is migrated to [AraViQ6](https://pypi.org/project/araviq6/).

# Introduction

`PySide6` provides powerful tools to acquire video stream from file or device, and to display it on GUI.
`cv2` is a de facto standard module for image analysis with Python.
It is natural to process the image with `cv2` and display it using `PySide6`.

`cv2PySide6` is a package to help build the video frame pipeline for this purpose.
It provides the object to convert `PySide6.QVideoFrame` to `numpy.ndarray`, and widget to directly display the array.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless `OpenCV-Python` modifies the Qt dependency thus making `PySide6` unavailable.

`cv2PySide6` can be installed using `pip`.

```
$ pip install cv2PySide6
```

# How to use

User can construct a pipeline which converts `QVideoFrame` to `ndarray`, performs any desired processing and displays to the widget.

<div align="center">
  <img src="https://github.com/JSS95/cv2PySide6/raw/master/doc/source/_images/pipeline.png"/><br>
    Video display pipeline
</div>

## `QVideoFrame` to `ndarray`

`QVideoFrame` is acquired from media file (`PySide6.QMediaPlayer`) or camera capture session (`PySide6.QMediaCaptureSession`) by setting `PySide6.QVideoSink` to them and listening to `QVideoSink.videoFrameChanged` signal.

To convert it, pass the video frame `cv2PySide6.FrameToArrayConverter` and listen to `FrameToArrayConverter.arrayChanged` signal.

> (Note) If you want to convert a single `PySide6.QImage` to `ndarray`, [qimage2ndarray](https://pypi.org/project/qimage2ndarray/) package provides handy functions.

## Displaying `ndarray`

`cv2PySide6.NDArrayLabel` is a widget to directly display `ndarray`.
It can also scale the image with respect to the widget size, and user can select the scaling mode.

## Convenience classes

For convenience, `cv2PySide6` provides `NDArrayVideoPlayer` and `NDArrayMediaCaptureSession` which inherits their `PySide6` counterparts and emits `arrayChanged` signal.
`NDArrayVideoPlayerWidget` and `NDArrayCameraWidget` are the minimal implementation to display the video stream with them.

However, time-consuming image processing will block the GUI with these classes because they use a single thread.
To build multithread pipeline, refer to the examples and build the pipeline yourself.

# Examples

Use cases with multithreading are provided in [examples](https://github.com/JSS95/cv2PySide6/tree/master/cv2PySide6/examples) directory.
They can be found in documentation as well.

# Documentation

Documentation can be found on Read the Docs:

> https://cv2pyside6.readthedocs.io/

If you want to build the document yourself, clone the source code and install with `[doc]` option.
Go to `doc` directory and build.

```
$ pip install cv2PySide6[doc]
$ cd doc
$ make html
```
