import pyaudio
import numpy as np
import threading
import queue
import time
import os
import string
import tempfile
from openai import OpenAI
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
RECORD_SECONDS = 5

class VoiceChat:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.q = queue.Queue()
        self.listening = threading.Event()
        self.recording = threading.Event()
        self.wake_phrase = 'delphi wake the hell up'
        self.stream = None
        self.client = OpenAI()

    def start(self):
        if not self.listening.is_set():
            self.listening.set()
            self._open_stream()
            threading.Thread(target=self.listen_function, daemon=True).start()
            print("Voice chat enabled")
        else:
            print("Voice chat is already enabled")

    def _open_stream(self):
        self.stream = self.p.open(format=FORMAT,
                                  channels=CHANNELS,
                                  rate=RATE,
                                  input=True,
                                  frames_per_buffer=CHUNK)

    def listen_function(self):
        last_command_time = time.time()
        silence_timeout = 5
        buffer = []
        buffer_duration = 2

        while self.listening.is_set():
            try:
                audio_data = self.stream.read(CHUNK, exception_on_overflow=False)
                buffer.append(audio_data)

                if len(buffer) * CHUNK >= RATE * buffer_duration:
                    audio_data = b''.join(buffer)
                    text = self.process_audio_text(audio_data)
                    buffer = []  

                    if text:
                        last_command_time = time.time()
                        if text.lower().translate(str.maketrans("", "", string.punctuation)) == self.wake_phrase:
                            print("Wake phrase detected. Listening for commands...")
                            self.record_and_process()
                        else:
                            print(f"Heard: {text}")
                    else:
                        if time.time() - last_command_time > silence_timeout:
                            print("No command detected in the last 5 seconds. Stopping listen function.")
                            self.listening.clear()
                            break
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    print("Input overflowed, discarding data")
                    self.stream.read(self.stream.get_read_available(), exception_on_overflow=False)
                else:
                    print(f"IOError in listen_function: {e}")
            except Exception as e:
                print(f"Error in listen_function: {e}")
                self.listening.clear()

        print("Listen function has stopped.")

    def record_and_process(self):
        self.recording.set()
        frames = []
        print("Recording your commands good sir...")
        start_time = time.time()
        while self.recording.is_set() and time.time() - start_time < RECORD_SECONDS:
            try:
                data = self.stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except IOError as e:
                if e.errno == pyaudio.paInputOverflowed:
                    print("Input overflowed during recording, discarding data")
                    self.stream.read(self.stream.get_read_available(), exception_on_overflow=False)
                else:
                    print(f"IOError during recording: {e}")
            except Exception as e:
                print(f"Error during recording: {e}")
                break
        print("Recording finished.")
        self.recording.clear()

        if frames:
            audio_data = b''.join(frames)
            transcribed_text = self.process_audio_text(audio_data)
            
            if transcribed_text:
                print(f"You said: {transcribed_text}")
                # TODO: Add the appropriate GPT function here
                # response = self.gpt_function(transcribed_text)
                # print(f"Assistant: {response}")
            else:
                print("Not clear")

    def process_audio_text(self, audio_data):
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmpfile:
            wf = wave.open(tmpfile.name, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(self.p.get_sample_size(FORMAT))
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
                return transcription
            except Exception as e:
                print(f"Error in transcription: {e}")
                return ""
            finally:
                os.unlink(tmpfile.name)

    def stop(self):
        self.listening.clear()
        self.recording.clear()
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        self.p.terminate()
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