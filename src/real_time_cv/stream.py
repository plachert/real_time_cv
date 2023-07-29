"""This module implements streams that can be used with webrtc_streamer."""
from __future__ import annotations

import cv2
import numpy as np
from aiortc.mediastreams import VideoStreamTrack
from av import VideoFrame


class InconsistentFramesShapes(Exception):
    pass


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
        frame = VideoFrame.from_ndarray(frame, 'bgr24')
        frame.pts = pts
        frame.time_base = time_base
        return frame


class FromImagesStreamTrack(VideoStreamTrack):
    """
    Generate frames from images provided as a saved numpy array (N, H, W, C).
    """

    def __init__(self, filenames):
        super().__init__()
        self.counter = 0
        self.image_idx = 0
        self.frames = self._frames_from_filenames(filenames)
        self.frames = [
            VideoFrame.from_ndarray(
                frame, 'bgr24',
            ) for frame in self.frames
        ]

    def _frames_from_filenames(self, filenames):
        frames = [
            cv2.imread(filename)[..., :3]
            for filename in filenames
        ]  # remove alpha if png
        shape = frames[0].shape
        for frame in frames:
            if shape != frame.shape:
                raise InconsistentFramesShapes
        return np.array(frames)

    async def recv(self):
        pts, time_base = await self.next_timestamp()
        if not self.counter % 100:
            self.image_idx += 1
            self.image_idx = self.image_idx % len(self.frames)
        frame = self.frames[self.image_idx]
        frame.pts = pts
        frame.time_base = time_base
        self.counter += 1
        return frame
