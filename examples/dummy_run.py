from real_time_cv.processing import ProcessorPlugin
from real_time_cv.app import run
import av
import cv2
import time


def identity(frame: av.VideoFrame) -> av.VideoFrame:
    return frame

def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    time.sleep(1)
    return av.VideoFrame.from_ndarray(gray, format="gray")

if __name__ == "__main__":
    dummy_plugin = ProcessorPlugin()
    dummy_plugin.register_ref_processor(identity)
    dummy_plugin.register_processor("convert to gray", convert2gray)
    run(dummy_plugin)