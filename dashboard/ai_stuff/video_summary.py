from moviepy import VideoFileClip
import ollama
from faster_whisper import WhisperModel
from fastapi import WebSocket
import time
from pydub import AudioSegment

class VideoSummarizer():

    def __init__(self, video_path,model,prompt):

        self.start_time = time.time()
        self.video_path = video_path
        self.model = model
        self.prompt = prompt
    
  
    def transcription_worker(self,video_path,context_buffer):
        segments, _ = self.model.transcribe(video_path,word_timestamps=True)

        for segment in segments:
            context_buffer.add_text(segment.text)

    def llm_worker(self,context_buffer,webapp_queue):
        while True:
            current_context = context_buffer.get_context()
            llm_response = self.process_with_llm(current_context)
            webapp_queue.put(llm_response)
            time.sleep(0.5)
    
    def webapp_worker(self,webapp_queue):
        while True:
            if not webapp_queue.empty():
                print(webapp_queue.get())
    

    def process_with_llm(self,current_context):

        curr_prompt = f"{self.prompt}: {current_context}"
        response = ollama.chat(model="llama3.2:1b", messages=[
            {"role": "user", "content":curr_prompt}
        ])
        return response["message"]["content"]

   

    def transcribe_video(self,audio_path):

        model = WhisperModel("tiny.en",device="cpu",compute_type="int8",cpu_threads=4)
        segments,_ = model.transcribe(audio_path,beam_size=3,chunk_length=20,without_timestamps=True,no_speech_threshold=0.4)

        return " ".join([segment.text for segment in segments])

   
    def extract_audio(self):

        video = VideoFileClip(self.video_path)
        audio_path = self.video_path.replace("static/videos/", "static/audio/").replace(".mp4", ".wav")
        video.audio.write_audiofile(audio_path, codec="pcm_s16le")
        audio = AudioSegment.from_file(audio_path,format="wav")
        audio = audio.set_frame_rate(16000)
        audio = audio.set_channels(1)
        audio.export(audio_path, format="wav")
        print(f"audios : {audio.channels}")

        # self.convert_to_16k(f"{os.get_cwd()}\\{audio_path}",f"{os.get_cwd()}\\{replaced_path}")
        return audio_path
    
    def generate_summary(self,transcript):

        self.prompt = f"{self.prompt}: {transcript}"
        response = ollama.chat(model=self.model, messages=[
            {"role": "user", "content":self.prompt}
        ])
        return response["message"]["content"]

    async def analyze_video(self,websocket:WebSocket):

        try:
            await websocket.send_text("Task started")
            audio_path = self.extract_audio()
            await websocket.send_text("progress: 33")
            transcript = self.transcribe_video(audio_path)
            await websocket.send_text("progress: 34")
            summary = self.generate_summary(transcript)
            await websocket.send_text("progress: 33")

            time.sleep(1)
            total_time_elapsed = time.time() - self.start_time

            await websocket.send_json({"status":"completed","summary":summary,"time_elapsed_sec":total_time_elapsed})
            # return summary,total_time_elapsed
        
        except Exception as e:

            return f"{e}"
       