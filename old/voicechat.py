""" This file includes a test of the voice chat feature via OpenAI. """

from GPT_function_calling import OpenAI
import os
from dotenv import load_dotenv
import pyaudio
import wave

def get_input_audio():
    """ Function that gets the user's input audio. """
    
    print("Please speak into the microphone.")
    
    chunk = 1024  # Record in chunks of 1024 samples
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    rate = 44100  # Record at 44100 samples per second

    p = pyaudio.PyAudio()  # Create an interface to PortAudio
    
    stream = p.open(format=sample_format,
                channels=channels,
                rate=rate,
                frames_per_buffer=chunk,
                input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    seconds = 3
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()
    
    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()
    


def chat():
    """ Function that handles user voice to voice chat with OpenAI. """
    
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    
    input_speech = get_input_audio()
    output_speech = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful computer assistant who does tasks on the computer for the user make your best attempt to help the user with using their computer, act like you have access to open files, search, and take other actions related to the computer. DO NOT MENTION ANYTHING ELSE."},
            {"role": "user", "content": input_speech}
        ]
    )
    
    print(output_speech.choices[0].message.content)
    
    response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=output_speech.choices[0].message.content
    )
    
    # This is supposedly deprecated, but the other methods I
    # tried didn't work immediately. Will stick with this for now.
    response.stream_to_file("response.mp3")

# This is just there so I can avoid wasting credits.
print("Would you like to chat with me? (yes/no):")

response = input()
if response == "yes":
    get_input_audio()
    # chat()
