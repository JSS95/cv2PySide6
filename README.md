Python package to combine `OpenCV-Python` and `PySide6`.

# Introduction

`cv2PySide6` is a package to display image or video from `numpy.ndarray` using `PySide6`.
It helps the user to process the image with `cv2` and visualize the result with `PySide6` GUI.

# Installation

Before you install, be careful for other Qt-dependent packages installed in your environment.
For example, non-headless `OpenCV-Python` modifies the Qt dependency thus making `PySide6` unavailable.

`cv2PySide6` can be installed using `pip`.

```
$ pip install cv2PySide6
```

# How to use

## Single image

`NDArrayLabel` is a label which can directly display `numpy.ndarray` object.
Pass the processed image directly to `NDArrayLabel.setArray`.

## Video

`NDArrayVideoPlayerWidget` provides video pipeline which converts video frame to numpy array, process, and display.

# Examples

Use cases are provided in [examples](https://github.com/JSS95/cv2PySide6/tree/master/cv2PySide6/examples) directory.
