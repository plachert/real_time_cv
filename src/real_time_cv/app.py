import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer
from stream import FromFileVideoStreamTrack


# Main streamlit application
def main():
    st.title("Video Stream from File")

    # Select video file
    video_file = "/home/piotr/github/real_time_cv/test.mp4"

    if video_file is not None:
        # Create video track from the selected file
        video_track = FromFileVideoStreamTrack(video_file)#VideoFileTrack(video_file)

        # Create WebRTC streamer
        webrtc_streamer(
            key="video-file-stream",
            source_video_track=video_track,
            media_stream_constraints={"video": True, "audio": False},
        )

# Run the application
if __name__ == "__main__":
    main()
