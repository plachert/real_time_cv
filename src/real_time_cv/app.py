import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from stream import FromFileVideoStreamTrack
import tempfile
import av
import cv2
import time
import threading

sync_event = threading.Event()

def synchronize_processors(ref_processor, processor):
    def ref_processor_wrapper(*args):
        sync_event.wait()
        result = ref_processor(*args)
        sync_event.clear()
        return result
    def processor_wrapper(*args):
        result = processor(*args)
        sync_event.set()
        return result
    return ref_processor_wrapper, processor_wrapper


def make_raw_stream(mode, source_video_track):
    with st.sidebar:
        ctx = webrtc_streamer(
            key="stream-org",
            mode=mode,
            source_video_track=source_video_track,
            desired_playing_state=DESIRED_PLAYING_STATE,
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration=ICE_CONFIG,
            video_html_attrs={"hidden": True},
            )
    return ctx

def make_processors_view(raw_stream, ref_processor, processor):
    col_reference, col_processor = st.columns(2)
    with col_reference:
        webrtc_streamer(
            key="stream-reference",
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=ref_processor,
            source_video_track=raw_stream.output_video_track,
            desired_playing_state=raw_stream.state.playing,
            rtc_configuration=ICE_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
        )
    with col_processor:
        webrtc_streamer(
            key=f"stream-processor",
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=processor,
            source_video_track=raw_stream.output_video_track,
            desired_playing_state=raw_stream.state.playing,
            rtc_configuration=ICE_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
        )
        


ICE_CONFIG = {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
DESIRED_PLAYING_STATE = True


def identity(frame: av.VideoFrame) -> av.VideoFrame:
    return frame

def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    time.sleep(1)
    return av.VideoFrame.from_ndarray(gray, format="gray")
        
        
available_processors = {
    "identity": identity,
    "convert2gray": convert2gray,
}


def main():
    method = st.sidebar.radio('Select stream', options=['Webcam', 'File'])
    processor_name = st.sidebar.selectbox("Select Processors:", list(available_processors.keys())) 
    processor = available_processors[processor_name]
    ref_processor = identity # Tu bedzie mozliwosc ustawienia z zewnatrz
    is_sync = st.sidebar.checkbox("Synchronize processors")
    if is_sync:
        ref_processor, processor = synchronize_processors(ref_processor, processor)
    is_stream = False
    if method == "File":
        video_file = st.sidebar.file_uploader("Upload a video file", type=["mp4", "avi"])
        if video_file:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(video_file.read())
            temp_file.close()
            source_video_track = FromFileVideoStreamTrack(temp_file.name)
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
        )
        make_processors_view(
            raw_stream=raw_stream,
            ref_processor=ref_processor,
            processor=processor
        )

# Run the application
if __name__ == "__main__":
    main()
