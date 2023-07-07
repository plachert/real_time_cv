import threading
import av
import cv2
import time

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

def identity(frame: av.VideoFrame) -> av.VideoFrame:
    return frame

def convert2gray(frame: av.VideoFrame) -> av.VideoFrame:
    image = frame.to_ndarray(format="bgr24")
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    time.sleep(1)
    return av.VideoFrame.from_ndarray(gray, format="gray")


class ProcessorPlugin:
    def __init__(self):
        self._ref_processor = None
        self._processors = {}
        
    @property
    def ref_processor(self):
        if self._ref_processor is None:
            Warning("Register the ref_processor first.")
        else:
            return self._ref_processor 
    
    @property
    def available_processors(self):
        if self._processors:
            return self._processors
        else:
            Warning("Register some processors first.")
        
    def register_ref_processor(self, processor):
        self._ref_processor = processor
            
    def register_processor(self, name, processor):
        if self._processors.get(name):
            Warning("Processor with such name already exists. ")
            return
        self._processors[name] = processor


dummy_plugin = ProcessorPlugin()
dummy_plugin.register_ref_processor(identity)
dummy_plugin.register_processor("convert to gray", convert2gray)
