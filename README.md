# Real Time CV
Streamlit app based on [streamlit-webrtc](https://github.com/whitphx/streamlit-webrtc/tree/main) for visualising CV (Computer Vision) tasks in real time.

![](https://github.com/plachert/real_time_cv/blob/main/examples/yolov8.gif)

## Table of Contents
* [Description](#description)
    * [Streams](#streams)
    * [Processors](#processors)
* [Getting Started](#getting-started)
    * [Installing](#installing)
    * [Examples](#examples)


##  Description
The main goal of the app is to enable quick evaluation of CV models on real data in real time. It also provides an easy way to compare two models (or any other image processing) on real-time data by using a synchronization mechanism and displaying them side by side.

The application is supposed to be used as an installable package with processing functions being registered by the user (see [Processors](#processors)).

### Streams
Three types of streams can be used as an input:
- Webcam
- File (video file that serves as a looped stream of frames)
- Images (this will create a video like stream of images, each image will be displayed for 100 frames). All uploaded images should be of the same size.

Currently streams are a fixed part of the code, that the user has no control over. If the provided solution turns out not to be flexible enough, it can be easily changed (please submit an issue if that is the case).

### Processors
Processors are functions that operate on a frame (`av.VideoFrame`) and return a processed frame (also `av.VideoFrame`). They are supposed to be provided by the user in ProcessorPlugin (see [Examples](#examples)). These functions serve as video callbacks in `webrtc-streamer` object and run in separate threads.

`ref_processor` - the output of this processor is labeled as *Reference*

`processor` - there can be more than one. They will show up in the selectbox `"Select processor"`. The output of this processor is labeled as *Processed*

The processed streams are independent unless we use synchronization mechanism (checkbox `"Synchronize processors"`). When it is checked the reference processor will wait for the other processor. This might be useful when comparing the quality of processors. Currently the synchronization is not symmetrical, which implies that the reference processor should outperform the other processor.

## Getting Started

### Installing
Run the following command in your virtual env.

```shell
pip install git+https://github.com/plachert/real_time_cv
```

Verify installation:
```shell
(venv) foo@bar:~$ python
>>> import real_time_cv
>>> real_time_cv.__version__
'1.1.0`
>>>
```

### Examples
1. Run this simple configuration as a streamlit app `streamlit run example.py`
```python
from __future__ import annotations

import time

import av
import cv2
from real_time_cv.app import run, DEFAULT_ICE_CONFIG
from real_time_cv.processing import ProcessorPlugin


def identity(frame: av.VideoFrame) -> av.VideoFrame:
    return frame


def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format='bgr24')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    time.sleep(1) # simulate heavy processing
    return av.VideoFrame.from_ndarray(gray, format='gray')


if __name__ == '__main__':
    dummy_plugin = ProcessorPlugin()
    dummy_plugin.register_ref_processor(identity) # There can be only one ref_processor
    dummy_plugin.register_processor('convert to gray', convert2gray) # There can be more than one
    run(
        processor_plugin=dummy_plugin,
        rtc_configuration=DEFAULT_ICE_CONFIG, # you can set your own rtc config (check https://github.com/whitphx/streamlit-webrtc/tree/main)
        layout='vertical', # this controls the layout of the streams (ref/processor) ['vertical', 'horizontal']
        )
```

2. Here is a more practical example - semantic segmentation with YOLOv8. It requires ultralytics - `pip install ultralytics` and a trained model (`examples/yolo_seg_model.pt`)

```python
from __future__ import annotations

from pathlib import Path

import av
import streamlit as st
from real_time_cv.app import run
from real_time_cv.processing import ProcessorPlugin
from ultralytics import YOLO

HERE = Path(__file__).parent

if 'model' in st.session_state:
    model = st.session_state['model']
else:
    model_path = HERE / 'yolo_seg_model.pt'
    model = YOLO(model_path)
    st.session_state['model'] = model


def identity(frame: av.VideoFrame) -> av.VideoFrame:
    return frame


def yolov8_segmentation(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format='bgr24')
    result = model(image)[0].plot()
    return av.VideoFrame.from_ndarray(result, format='bgr24')


if __name__ == '__main__':
    dummy_plugin = ProcessorPlugin()
    # There can be only one ref_processor
    dummy_plugin.register_ref_processor(identity)
    dummy_plugin.register_processor(
        'yolov8_segmentation', yolov8_segmentation,
    )  # There can be more than one
    run(dummy_plugin)

```

## Licence

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/plachert/real_time_cv/blob/main/LICENSE)
