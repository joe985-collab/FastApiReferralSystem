from faster_whisper import WhisperModel
from collections import deque
import time
import ollama
import threading


class LowLatencySummarizer:

    def __init__(self,window_size=120,overlap=100):
        self.buffer = deque(maxlen=window_size)
        self.window_size = window_size
        self.overlap = overlap
        self.lock = threading.Lock()

    def add_text(self,text):
        with self.lock:
            self.buffer.extend(text.split())

    def get_context(self):
        with self.lock:
            start_idx = max(0,len(self.buffer)-self.window_size)
            end_idx = len(self.buffer)
            return " ".join(list(self.buffer)[start_idx:end_idx])
    

    
        