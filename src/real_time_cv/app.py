import cv2
import streamlit as st
from streamlit_webrtc import webrtc_streamer
from stream import FromFileVideoStreamTrack
import tempfile


# Main streamlit application
def main():
    st.title("Video Stream from File")
    method = st.sidebar.radio('Select stream', options=['Webcam', 'File'])

    # Select video file
    # video_file = "/home/piotr/github/real_time_cv/test.mp4"


    if method == "File":
        # Create video track from the selected file
        video_file = st.file_uploader("Upload a video file", type=["mp4", "avi"])
        if video_file is not None:
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            temp_file.write(video_file.read())
            temp_file.close()
            # Create video track from the saved file
            video_track = FromFileVideoStreamTrack(temp_file.name)

            # Create WebRTC streamer
            webrtc_streamer(
                key="video-file-stream",
                source_video_track=video_track,
                media_stream_constraints={"video": True, "audio": False},
        )
    else:
        webrtc_streamer(
            key="camera-stream",
            media_stream_constraints={"video": True, "audio": False},
        )

# Run the application
if __name__ == "__main__":
    main()
