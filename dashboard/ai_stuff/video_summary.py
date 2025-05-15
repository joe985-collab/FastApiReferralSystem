from moviepy import VideoFileClip
import ollama
from faster_whisper import WhisperModel
import os
import time

class VideoSummarizer():

    def __init__(self, video_path,model,prompt):

        self.start_time = time.time()
        self.video_path = video_path
        self.model = model
        self.prompt = prompt
    
    def transcribe_video(self,audio_path):

        model = WhisperModel("base",device="cpu",compute_type="int8")

        segments,_ = model.transcribe(audio_path,beam_size=5,chunk_length=20)

        return " ".join([segment.text for segment in segments])

    def extract_audio(self):

        video = VideoFileClip(self.video_path)
        audio_path = self.video_path.replace("static/videos/", "static/audio/").replace(".mp4", ".wav")
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")
        return audio_path
    
    def generate_summary(self,transcript):

        self.prompt = f"{self.prompt}: {transcript}"
        response = ollama.chat(model=self.model, messages=[
            {"role": "user", "content":self.prompt}
        ])
        return response["message"]["content"]

    def analyze_video(self):

        # try:

            audio_path = self.extract_audio()
            transcript = self.transcribe_video(audio_path)
            summary = self.generate_summary(transcript)
            total_time_elapsed = time.time() - self.start_time


            return summary,total_time_elapsed
        
        # except Exception as e:

        #     return f"{e}"