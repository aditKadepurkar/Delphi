import sounddevice as sd
import numpy as np
import threading
import queue
import time
from openai import OpenAI
from dotenv import load_dotenv
import os
import wave
import tempfile
import whisper
from gtts import gTTS
from playsound import playsound

CHANNELS = 1
RATE = 16000  # Whisper models expect 16kHz audio
CHUNK = 1024
RECORD_SECONDS = 3
SILENCE_THRESHOLD = 5

class WakeWordAssistant:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.listening = threading.Event()
        self.wake_phrase = "hello"
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.whisper_model = whisper.load_model("base")  # Load the Whisper model

    def start(self):
        self.listening.set()
        threading.Thread(target=self.listen_for_wake_word).start()
        print("Wake word assistant enabled")

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Status: {status}")
        self.audio_queue.put(indata.copy())

    def is_speech(self, audio_data, energy_threshold=0.003, zero_crossing_threshold=0.015):
        # Improved speech detection using energy and zero-crossing rate
        start_time = time.time()

        print("start_time", start_time)
        energy = np.sum(np.square(audio_data)) / len(audio_data)
        zero_crossings = np.sum(np.abs(np.diff(np.sign(audio_data)))) / (2 * len(audio_data))

        execution_time = time.time() - start_time 
        
        print("execution_time", execution_time)
        return energy > energy_threshold and zero_crossings > zero_crossing_threshold
    
    def listen_for_wake_word(self):
        print("Listening for wake word...")
        audio_buffer = []
        buffer_duration = 3  # seconds
        samples_per_buffer = int(RATE * buffer_duration)
        silence_timeout = 3  # seconds
        last_speech_time = time.time()

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            audio_buffer.extend(indata.flatten())
            
            # Keep only the last 'buffer_duration' seconds of audio
            if len(audio_buffer) > samples_per_buffer:
                del audio_buffer[:len(audio_buffer) - samples_per_buffer]

        

        try:
            with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=RATE, dtype=np.int16):
                print("Listening... Press Ctrl+C to stop.")
                while self.listening.is_set():
                    if len(audio_buffer) >= samples_per_buffer:
                        audio_data = np.array(audio_buffer)
                        if self.is_speech(audio_data=audio_data):
                            text = self.transcribe_whisper(audio_data)
                            if text and text.strip():  # Only print if text is not empty
                                print(f"Transcribed: {text}")
                                last_speech_time = time.time()
                                if self.wake_phrase in text.strip().lower():
                                    print("Wake word detected. Activating assistant.")
                                    break
                        elif time.time() - last_speech_time > silence_timeout:
                            audio_buffer.clear()
                            last_speech_time = time.time()
                    time.sleep(0.1)
            self.process_commands()
        except KeyboardInterrupt:
            print("\nStopped listening for wake word.")
        except Exception as e:
            print(f"Error in listen_for_wake_word: {e}")

    
    def transcribe_whisper(self, audio_data):
        try:
            # Save audio data to a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                with wave.open(temp_audio.name, "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)  # 2 bytes per sample for np.int16
                    wf.setframerate(RATE)
                    wf.writeframes(audio_data.tobytes())
                
                # Use Whisper (its free) to transcribe the audio
                result = self.whisper_model.transcribe(temp_audio.name, fp16=False)
                text = result["text"].strip()

            os.unlink(temp_audio.name)  # Delete the temporary file

            return text
        except Exception as e:
            print(f"Error in transcribe_audio: {e}")
        return None

    def transcribe_openai(self, audio_data):
        try:
            # Save audio data to a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_audio:
                with wave.open(temp_audio.name, "wb") as wf:
                    wf.setnchannels(CHANNELS)
                    wf.setsampwidth(2)  # 2 bytes per sample for np.int16
                    wf.setframerate(RATE)
                    wf.writeframes(audio_data.tobytes())
                
                # Use Whisper (its free) to transcribe the audio
                audio_file= open(temp_audio.name, "rb")
                result = self.client.audio.transcriptions.create(model="whisper-1", file=audio_file)
                text = result.text.strip()

            os.unlink(temp_audio.name)  # Delete the temporary file

            return text
        except Exception as e:
            print(f"Error in transcribe_audio: {e}")
        return None
        
    def text_to_speech(self, text):
        try:
            tts = gTTS(text=text, lang="en")
            tts.save("speech.mp3")
            playsound("speech.mp3")
        except Exception as e:
            print(f"Error in text_to_speech: {e}")
    
    def process_commands(self):
        print("Assistant activated. Listening for commands...")
        audio_buffer = []
        buffer_duration = 3  # seconds
        samples_per_buffer = int(RATE * buffer_duration)
        silence_timeout = 3  # seconds
        last_speech_time = time.time()
        consecutive_silence_count = 0

        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Status: {status}")
            audio_buffer.extend(indata.flatten())
            
            # Keep only the last 'buffer_duration' seconds of audio
            if len(audio_buffer) > samples_per_buffer:
                del audio_buffer[:len(audio_buffer) - samples_per_buffer]

        try:
            with sd.InputStream(callback=audio_callback, channels=CHANNELS, samplerate=RATE, dtype=np.int16):
                print("Listening... Press Ctrl+C to stop.")
                while self.listening.is_set():
                    if len(audio_buffer) >= samples_per_buffer:
                        audio_data = np.array(audio_buffer)
                        if self.is_speech(audio_data=audio_data):
                            text = self.transcribe_openai(audio_data)
                            if text.strip() != "":
                                print(f"User: {text}")
                                last_speech_time = time.time()
                                silence_duration = 0
                                
                                response = self.get_ai_response(text)
                                print(f"Assistant: {response}")
                                self.text_to_speech(response)
                                print('Good bye now.')
                                self.stop()
                                break
                                  # Implement this method for speech output
                            else :
                                consecutive_silence += 1
                        else:
                            consecutive_silence_count += 1

                        if consecutive_silence_count * buffer_duration >= silence_timeout:
                                print(f"No speech detected for {SILENCE_THRESHOLD} seconds. Listening for wake word again.")
                                self.listen_for_wake_word()
                                break

                    time.sleep(0.1)

        except Exception as e:
            print(f"Error in process_commands: {e}")
    
    def get_ai_response(self, user_input):
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_input}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error getting AI response: {e}")
            return "I'm sorry, I couldn't process that request."
    def test_recording(self):
        print("Recording for 5 seconds")
        audio_data = []
        duration = 5  # seconds
        audio_data = sd.rec(int(duration * RATE), samplerate=RATE, channels=CHANNELS, dtype=np.int16)
        sd.wait()
        try:
           
            audio_data = np.concatenate(audio_data)
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            filename =  f"recording-{timestamp}.wav"
            with wave.open(filename, "wb") as wf:
                wf.setnchannels(CHANNELS)
                wf.setsampwidth(2)
                wf.setframerate(RATE)
                wf.writeframes(audio_data.tobytes())
        except Exception as e:
            print(f"Error during test recording: {e}")
        

    def stop(self):
        self.listening.clear()
        quit()
        print("Wake word assistant disabled.")

def main():
    assistant = WakeWordAssistant()
    print("Wake Word Assistant")
    print("Commands:")
    print("  start  - Activate the wake word assistant")
    print("  stop   - Deactivate the wake word assistant")
    print("  quit   - Exit the program")
    print("  record - Record audio for 5 seconds")
    command = input("Enter command: ").strip().lower()
    if command == 'start':
        assistant.start()
    elif command == 'stop':
        assistant.stop()
    elif command == 'quit':
        assistant.stop()
        print("Exiting program.")
        
    elif command == 'record':
        assistant.test_recording()
    else:
        print("Invalid command. Please try again.")

if __name__ == "__main__":
    main()