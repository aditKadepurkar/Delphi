""" This file includes a test of the voice chat feature via OpenAI. """

from openai import OpenAI
import os
from dotenv import load_dotenv

def get_input_audio():
    """ Function that gets the user's input audio. """
    
    print("Please speak into the microphone.")
    
    # Placeholder for the user's input audio.
    input_audio = "How are you?"
    
    return input_audio


def chat():
    """ Function that handles user voice to voice chat with OpenAI. """
    
    load_dotenv()
    os.getenv("OPENAI_API_KEY")
    client = OpenAI()
    
    input_speech = get_input_audio()
    output_speech = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful computer assistant who does tasks on the computer for the user."},
            {"role": "user", "content": input_speech}
        ]
    )
    
    print("34:", output_speech.choices[0].message.content)
    
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
    chat()
