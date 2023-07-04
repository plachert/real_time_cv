import cv2
from aiortc.mediastreams import VideoStreamTrack

from av import VideoFrame

class FromFileVideoStreamTrack(VideoStreamTrack):
    """
    Generate frames from video file.
    """
    def __init__(self, filename):
        super().__init__()  # don't forget this!
        self.cap = cv2.VideoCapture(filename)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        _, frame = self.cap.read()
        frame = VideoFrame.from_ndarray(frame, "bgr24")
        frame.pts = pts
        frame.time_base = time_base
        return frame
