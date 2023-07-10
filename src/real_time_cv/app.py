from __future__ import annotations

import tempfile

import streamlit as st
from streamlit_webrtc import webrtc_streamer
from streamlit_webrtc import WebRtcMode

from .processing import dummy_plugin
from .processing import ProcessorPlugin
from .processing import synchronize_processors
from .stream import FromFileVideoStreamTrack
from .stream import FromImagesStreamTrack

DEFAULT_ICE_CONFIG = {
    'iceServers': [
        {'urls': ['stun:stun.l.google.com:19302']},
    ],
}
DESIRED_PLAYING_STATE = None


def make_raw_stream(
    mode,
    source_video_track,
    rtc_configuration,
):
    with st.sidebar:
        st.header('Raw Stream')
        ctx = webrtc_streamer(
            key='stream-org',
            mode=mode,
            source_video_track=source_video_track,
            desired_playing_state=DESIRED_PLAYING_STATE,
            media_stream_constraints={'video': True, 'audio': False},
            rtc_configuration=rtc_configuration,
        )
    return ctx


def make_processors_view(
    raw_stream,
    ref_processor,
    processor,
    rtc_configuration,
    layout,
):
    if layout == 'vertical':
        ref_container, proc_container = st.container(), st.container()
    else:
        ref_container, proc_container = st.columns(2)
    with ref_container:
        st.header('Reference')
        webrtc_streamer(
            key='stream-reference',
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=ref_processor,
            source_video_track=raw_stream.output_video_track,
            desired_playing_state=raw_stream.state.playing,
            rtc_configuration=rtc_configuration,
            media_stream_constraints={'video': True, 'audio': False},
        )
    with proc_container:
        st.header('Processed')
        webrtc_streamer(
            key='stream-processor',
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=processor,
            source_video_track=raw_stream.output_video_track,
            desired_playing_state=raw_stream.state.playing,
            rtc_configuration=rtc_configuration,
            media_stream_constraints={'video': True, 'audio': False},
        )


def save_file(uploaded_file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(uploaded_file.getbuffer())
    filename = temp_file.name
    return filename


def run(
    processor_plugin: ProcessorPlugin = dummy_plugin,
    rtc_configuration=DEFAULT_ICE_CONFIG,
    layout='vertical',
):
    ref_processor = processor_plugin.ref_processor
    available_processors = processor_plugin.available_processors
    method = st.sidebar.radio(
        'Select stream',
        options=['File', 'Webcam', 'Images'],
    )
    processor_name = st.sidebar.selectbox(
        'Select processor:', list(available_processors.keys()),
    )
    processor = available_processors[processor_name]
    ref_processor = ref_processor
    is_sync = st.sidebar.checkbox('Synchronize processors', value=False)
    if is_sync:
        ref_processor, processor = synchronize_processors(
            ref_processor, processor,
        )
    is_stream = False
    if method == 'File':
        video_file = st.sidebar.file_uploader(
            'Upload a video file', type=['mp4', 'avi'],
        )
        if video_file:
            filename = save_file(video_file)
            source_video_track = FromFileVideoStreamTrack(filename)
            mode = WebRtcMode.RECVONLY
            is_stream = True
    elif method == 'Images':
        images_file = st.sidebar.file_uploader(
            'Upload array of images', type=['npy'],
        )
        if images_file:
            filename = save_file(images_file)
            source_video_track = FromImagesStreamTrack(filename)
            mode = WebRtcMode.RECVONLY
            is_stream = True
    else:
        mode = WebRtcMode.SENDRECV
        source_video_track = None
        is_stream = True
    if is_stream:
        raw_stream = make_raw_stream(
            mode=mode,
            source_video_track=source_video_track,
            rtc_configuration=rtc_configuration,
        )
        make_processors_view(
            raw_stream=raw_stream,
            ref_processor=ref_processor,
            processor=processor,
            rtc_configuration=rtc_configuration,
            layout=layout,
        )
