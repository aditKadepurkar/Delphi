import sounddevice as sd
import numpy as np
import threading
import queue
import time
import os
import speech_recognition as sr
import tempfile
from openai import OpenAI
import wave
from dotenv import load_dotenv

CHUNK = 1024
FORMAT = np.int16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5
SILENCE_THRESHOLD = 5 

class VoiceChat:
    def __init__(self):
        self.q = queue.Queue()
        self.listening = threading.Event()
        self.recording = threading.Event()
        self.wake_phrase = 'hello'
        self.stream = None
        self.transcription = None
        self.recognizer = sr.Recognizer()
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
        buffer = []
        buffer_duration = 2

        print("Listening for wake word...")
        with sd.InputStream(callback=self.audio_callback, channels=CHANNELS, samplerate=RATE, dtype=FORMAT):
            while self.listening.is_set():
                if not self.q.empty():
                    audio_data = self.q.get()
                    buffer.append(audio_data)

                    if len(buffer) * CHUNK >= RATE * buffer_duration:
                        audio_buffer = b''.join(buffer)
                        audio_np = np.frombuffer(audio_buffer, dtype=np.int16)
                        audio_data = sr.AudioData(audio_np.tobytes(), RATE, 2)
                        buffer = []  

                        try:
                            text = self.recognizer.recognize_google(audio_data, language='pt', show_all=False)
                            if text:
                                text = text.lower()
                        except sr.UnknownValueError:
                            text = ""

                        if text and self.wake_phrase in text:
                            print("Wake phrase detected. Activating voice chat.")
                            self.activate_voice_chat()

        print("Listen function stopped.")

    def activate_voice_chat(self):
        last_speech_time = time.time()
        buffer = []
        buffer_duration = 2

        print("Voice chat activated. Listening for commands...")
        while self.listening.is_set():
            if not self.q.empty():
                audio_data = self.q.get()
                buffer.append(audio_data)

                if len(buffer) * CHUNK >= RATE * buffer_duration:
                    audio_buffer = b''.join(buffer)
                    audio_np = np.frombuffer(audio_buffer, dtype=np.int16)
                    audio_data = sr.AudioData(audio_np.tobytes(), RATE, 2)
                    buffer = []

                    try:
                        text = self.recognizer.recognize_google(audio_data, language='pt', show_all=False)
                        if text:
                            text = text.lower()
                            print(f"User said: {text}")
                            last_speech_time = time.time()
                            
                            response = self.process_command(text)
                            print(f"Assistant: {response}")
                            
                            # TODO: Implement text-to-speech for the response
                    except sr.UnknownValueError:
                        pass

            if time.time() - last_speech_time > SILENCE_THRESHOLD:
                print("No speech detected for 5 seconds. Listening for wake word again.")
                break

        print("Voice chat disabled by state.")

    def process_command(self, command):
        # TODO: Implement more sophisticated command processing
        # For now, we'll just echo the command
        return f"You said: {command}"

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(status)
        self.q.put(indata.copy())

    def stop(self):
        self.listening.clear()
        self.recording.clear()
        print("Voice chat disabled by command.")

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