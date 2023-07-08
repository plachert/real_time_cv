from __future__ import annotations

import tempfile
from functools import partial

import streamlit as st
from aiortc.contrib.media import MediaPlayer
from streamlit_webrtc import webrtc_streamer
from streamlit_webrtc import WebRtcMode

from .processing import dummy_plugin
from .processing import ProcessorPlugin
from .processing import synchronize_processors
# from .stream import FromFileVideoStreamTrack

ICE_CONFIG = {'iceServers': [{'urls': ['stun:stun.l.google.com:19302']}]}
DESIRED_PLAYING_STATE = None


def make_raw_stream(mode, source_video_track, player_factory=None):
    with st.sidebar:
        ctx = webrtc_streamer(
            key='stream-org',
            mode=mode,
            source_video_track=source_video_track,
            desired_playing_state=DESIRED_PLAYING_STATE,
            player_factory=player_factory,
            media_stream_constraints={'video': True, 'audio': False},
            rtc_configuration=ICE_CONFIG,
            video_html_attrs={'hidden': True},
        )
    return ctx


def make_processors_view(raw_stream, ref_processor, processor):
    col_reference, col_processor = st.columns(2)
    with col_reference:
        webrtc_streamer(
            key='stream-reference',
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=ref_processor,
            source_video_track=raw_stream.output_video_track,
            desired_playing_state=raw_stream.state.playing,
            rtc_configuration=ICE_CONFIG,
            media_stream_constraints={'video': True, 'audio': False},
        )
    with col_processor:
        webrtc_streamer(
            key='stream-processor',
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=processor,
            source_video_track=raw_stream.output_video_track,
            desired_playing_state=raw_stream.state.playing,
            rtc_configuration=ICE_CONFIG,
            media_stream_constraints={'video': True, 'audio': False},
        )


def run(processor_plugin: ProcessorPlugin):
    ref_processor = processor_plugin.ref_processor
    available_processors = processor_plugin.available_processors
    method = st.sidebar.radio(
        'Select stream',
        options=['File', 'Webcam'],
    )
    processor_name = st.sidebar.selectbox(
        'Select Processors:', list(available_processors.keys()),
    )
    processor = available_processors[processor_name]
    ref_processor = ref_processor
    is_sync = st.sidebar.checkbox('Synchronize processors')
    if is_sync:
        ref_processor, processor = synchronize_processors(
            ref_processor, processor,
        )
    is_stream = False
    if method == 'File':
        video_file = st.sidebar.file_uploader(
            'Upload a video file', type=['mp4', 'avi'],
        )
        filename = None
        if video_file:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(video_file.getbuffer())
            is_stream = True
            filename = temp_file.name
        source_video_track = None
        player_factory = partial(MediaPlayer, filename)
        mode = WebRtcMode.RECVONLY
    else:
        mode = WebRtcMode.SENDRECV
        source_video_track = None
        player_factory = None
        is_stream = True
    if is_stream:
        raw_stream = make_raw_stream(
            mode=mode,
            source_video_track=source_video_track,
            player_factory=player_factory,
        )
        make_processors_view(
            raw_stream=raw_stream,
            ref_processor=ref_processor,
            processor=processor,
        )


if __name__ == '__main__':
    run(dummy_plugin)
