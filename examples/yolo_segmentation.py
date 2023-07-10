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
