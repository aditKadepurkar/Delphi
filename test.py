import sounddevice as sd

def callback(indata, frames, time, status):
    if status:
        print(status)

# This function will start recording audio from the microphone for 5 seconds
def record_audio():
    print("Recording for 5 seconds... Please allow microphone access.")
    try:
        # Start recording with a sample rate of 44100 Hz and 1 channel (mono)
        with sd.InputStream(callback=callback, channels=1, samplerate=44100):
            sd.sleep(5000)  # Record for 5 seconds
        print("Recording complete.")
    except Exception as e:
        print(f"Error accessing microphone: {e}")

if __name__ == "__main__":
    record_audio()
