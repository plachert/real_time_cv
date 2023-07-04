import streamlit as st
from streamlit_webrtc import webrtc_streamer
from stream import FromFileVideoStreamTrack, Dummy
import tempfile
import av
import numpy as np
import cv2

def identity(frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        return frame

def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        print("RUN")
        return av.VideoFrame.from_ndarray(gray, format="gray")

        # if model is None:
        #     return image

        # orig_h, orig_w = image.shape[0:2]

        # # cv2.resize used in a forked thread may cause memory leaks
        # input = np.asarray(Image.fromarray(image).resize((width, int(width * orig_h / orig_w))))

        # transferred = style_transfer(input, model)

        # result = Image.fromarray((transferred * 255).astype(np.uint8))
        # image = np.asarray(result.resize((orig_w, orig_h)))
        # return av.VideoFrame.from_ndarray(image, format="bgr24")
        
        
available_processors = {
    "identity": identity,
    "convert2gray": convert2gray,
}


# Main streamlit application
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
            # Create video track from the saved file
            video_track = FromFileVideoStreamTrack(temp_file.name)

            # Create WebRTC streamer
            webrtc_streamer(
                key="video-file-stream",
                source_video_track=video_track,
                media_stream_constraints={"video": True, "audio": False},
                video_frame_callback=processor,
        )
    else:
        webrtc_streamer(
            key="camera-stream",
            source_video_track=Dummy(),
            media_stream_constraints={"video": True, "audio": False},
            video_frame_callback=processor,
        )

# Run the application
if __name__ == "__main__":
    main()
