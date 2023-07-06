import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode
from stream import FromFileVideoStreamTrack
import tempfile
import av
import cv2


def identity(frame: av.VideoFrame) -> av.VideoFrame:
        return frame

def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return av.VideoFrame.from_ndarray(gray, format="gray")
        
        
available_processors = {
    "identity": identity,
    "convert2gray": convert2gray,
}


def main():
    st.title("Video Stream from File")
    method = st.sidebar.radio('Select stream', options=['Webcam', 'File'])
    processor_name = st.sidebar.selectbox("Select Processor:", list(available_processors.keys())) 
    processor = available_processors[processor_name]
    if method == "File":
        # Create video track from the selected file
        video_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
        if video_file is not None:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(video_file.read())
            temp_file.close()
            video_track = FromFileVideoStreamTrack(temp_file.name)
            webrtc_streamer(
                key="video-file-stream",
                mode=WebRtcMode.RECVONLY,
                source_video_track=video_track,
                media_stream_constraints={"video": True, "audio": False},
                video_frame_callback=processor,
                rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        )
    else:
        webrtc_streamer(
            key="camera-stream",
            source_video_track=None,
            media_stream_constraints={"video": True, "audio": False},
            video_frame_callback=processor,
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        )

# Run the application
if __name__ == "__main__":
    main()
