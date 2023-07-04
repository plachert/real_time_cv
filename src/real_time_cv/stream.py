"""This module implements streams that can be used with webrtc_streamer."""

import cv2
from aiortc.mediastreams import VideoStreamTrack
from av import VideoFrame


class Dummy(VideoStreamTrack):
    def __init__(self) -> None:
        super().__init__()
        

class FromFileVideoStreamTrack(VideoStreamTrack):
    """
    Generate frames from video file.
    """
    def __init__(self, filename):
        super().__init__()
        self.filename = filename
        self.cap = cv2.VideoCapture(filename)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        _, frame = self.cap.read()
        if frame is None:
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)  # Reset frame position
            _, frame = self.cap.read()
        frame = VideoFrame.from_ndarray(frame, "bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame
