# Real Time CV
Streamlit app based on [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc/tree/main) for visualising CV (Computer Vision) tasks in real time.

![](https://github.com/plachert/real_time_cv/blob/main/examples/yolov8.gif)

## Table of Contents
* [Description](#description)
    * [Streams](#streams)
    * [Processors](#processors)
* [Getting Started](#getting-started)
    * [Installing](#installing)
    * [Usage Examples](#usage-examples)


##  Description
The main goal of the app is to enable quick evaluation of CV models on real data in real time. It also provides an easy way to compare two models (or any other image processing) on real-time data by using a synchronization mechanism and displaying them side by side.

The application is supposed to be used as an installable package with processing functions being registered by the user (see [Processors](#processors)).

### Streams
Tree types of streams can be used as an input:
- Webcam
- File (video file that serves as a looped stream of frames)
- Images (this will create a video like stream of images, each image will be displayed for 100 frames)

Currently streams are a fixed part of the code, that the user has no control over. If the provided solution turns out not to be flexible enough, it can be easily changed (please submit an issue if that is the case).

### Processors
Processors are functions that operate on a frame (`av.VideoFrame`) and return a processed frame (also `av.Frame`). They are supposed to be provided by the user in ProcessorPlugin like so:

 ```python
 from __future__ import annotations

import time

import av
import cv2
from real_time_cv.app import run
from real_time_cv.processing import ProcessorPlugin


def identity(frame: av.VideoFrame) -> av.VideoFrame:
    return frame


def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format='bgr24')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    time.sleep(1)
    return av.VideoFrame.from_ndarray(gray, format='gray')


if __name__ == '__main__':
    dummy_plugin = ProcessorPlugin()
    dummy_plugin.register_ref_processor(identity) # There can be only one ref_processor
    dummy_plugin.register_processor('convert to gray', convert2gray) # There can be more than one
    run(dummy_plugin)
```

`ref_processor` - this will display frames on the left hand side (*Reference*)

`processor` - there can be more than one. They will show up in the selectbox `"Select processor"`. Displays on the right hand side (*Processed*)

## Getting Started

### Installing
Run the following command in your virtual env.

```shell
(venv) foo@bar:~$ pip install git+https://github.com/plachert/real_time_cv
```

Verify installation:
```shell
(venv) foo@bar:~$ python
>>> import real_time_cv
>>> real_time_cv.__version__
'1.0.0`
>>>
```

### Usage Examples

## Licence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/plachert/real_time_cv/blob/main/LICENSE)
