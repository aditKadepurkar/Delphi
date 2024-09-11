import sounddevice as sd
import numpy as np
import threading
import queue
import time
import os
import string
import tempfile
from openai import OpenAI
import wave
from dotenv import load_dotenv

CHUNK = 1024
FORMAT = np.int16  # Use NumPy data type
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5

class VoiceChat:
    def __init__(self):
        self.q = queue.Queue()
        self.listening = threading.Event()
        self.recording = threading.Event()
        self.wake_phrase = 'hello'
        self.stream = None
        self.transcription = None
        
        load_dotenv()
        os.getenv("OPENAI_API_KEY")
        
        self.client = OpenAI()
        self.frames = []

    def start(self):
        self.transcription = None
        if not self.listening.is_set():
            self.listening.set()
            threading.Thread(target=self.listen_function, daemon=True).start()
            print("Voice chat enabled")
        else:
            print("Voice chat is already enabled")

    def listen_function(self):
        last_command_time = time.time()
        silence_timeout = 5
        buffer = []
        buffer_duration = 2

        print("Listening for audio...")
        with sd.InputStream(callback=self.audio_callback, channels=CHANNELS, samplerate=RATE, dtype=FORMAT):
            while self.listening.is_set():
                if not self.q.empty():
                    audio_data = self.q.get()
                    buffer.append(audio_data)

                    if len(buffer) * CHUNK >= RATE * buffer_duration:
                        audio_data = b''.join(buffer)
                        text = self.process_audio_text(audio_data)
                        buffer = []  

                        if text:
                            last_command_time = time.time()
                            if text.lower().strip() == self.wake_phrase:
                                print("Wake phrase detected. Listening for commands...")
                                self.transcription = self.record_and_process()
                                self.stop()
                                return
                            # else:
                            #     print(f"Heard: {text}")
                        else:
                            if time.time() - last_command_time > silence_timeout:
                                print("No command detected in the last 5 seconds. Stopping listen function.")
                                self.listening.clear()
                                break

        print("Listen function has stopped.")

    def audio_callback(self, indata, frames, time, status):
        """Callback function to receive audio input"""
        if status:
            print(status)
        self.q.put(indata.copy())

    def record_and_process(self):
        self.recording.set()
        self.frames = []
        print("Recording your commands good sir...")
        start_time = time.time()
        while self.recording.is_set() and time.time() - start_time < RECORD_SECONDS:
            if not self.q.empty():
                self.frames.append(self.q.get())

        print("Recording finished.")
        self.recording.clear()

        if self.frames:
            audio_data = b''.join(self.frames)
            transcribed_text = self.process_audio_text(audio_data)

            if transcribed_text:
                return transcribed_text.lower().strip()
                # TODO: Add the appropriate GPT function here
                # response = self.gpt_function(transcribed_text)
                # print(f"Assistant: {response}")
            else:
                # print("Not clear")
                return "Failure"

    def process_audio_text(self, audio_data):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
            wf = wave.open(tmpfile.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(RATE)
            wf.writeframes(audio_data)
            wf.close()

            try:
                with open(tmpfile.name, "rb") as audio_file:
                    transcription = self.client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        response_format="text"
                    )
                    transcription = transcription.replace(',', '')
                    transcription = transcription.replace('.', '')
                    transcription = transcription.replace('?', '')
                    transcription = transcription.replace('!', '')
                return transcription
            except Exception as e:
                print(f"Error in transcription: {e}")
                return ""
            finally:
                os.unlink(tmpfile.name)

    def stop(self):
        self.listening.clear()
        self.recording.clear()
        print("Voice chat disabled")

def main():
    assistant = VoiceChat()
    print("Digital Assistant")
    print("Commands:")
    print("  start  - Activate the digital assistant")
    print("  quit   - Exit the program")

    while True:
        command = input("Enter command: ").strip().lower()

        if command == 'start':
            assistant.start()
        elif command == 'quit':
            assistant.stop()
            print("Exiting program.")
            break
        else:
            print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()
