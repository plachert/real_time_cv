import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from stream import FromFileVideoStreamTrack
import tempfile
import av
import cv2
import time


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
    processor_names = st.sidebar.multiselect("Select Processors:", list(available_processors.keys())) 
    
    if method == "File":
        video_file = st.sidebar.file_uploader("Upload a video file", type=["mp4", "avi"])
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.write(video_file.read())
        temp_file.close()
        video_track = FromFileVideoStreamTrack(temp_file.name)
        ctx = webrtc_streamer(
            key="stream-org",
            mode=WebRtcMode.RECVONLY,
            source_video_track=video_track,
            desired_playing_state=DESIRED_PLAYING_STATE,
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration=ICE_CONFIG,
            )
    else:
        ctx = webrtc_streamer(
            key="stream-org",
            source_video_track=None,
            desired_playing_state=DESIRED_PLAYING_STATE,
            media_stream_constraints={"video": True, "audio": False},
            rtc_configuration=ICE_CONFIG,
            )
    for i, processor_name in enumerate(processor_names):
        processor = available_processors[processor_name]
        webrtc_streamer(
            key=f"stream-{processor_name}",
            mode=WebRtcMode.RECVONLY,
            video_frame_callback=processor,
            source_video_track=ctx.output_video_track,
            desired_playing_state=ctx.state.playing,
            rtc_configuration=ICE_CONFIG,
            media_stream_constraints={"video": True, "audio": False},
        )


# Run the application
if __name__ == "__main__":
    main()
