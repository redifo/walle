import os
import openai
import pygame
import time
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile

# Function to record audio
def record_audio(duration=5, fs=44100):
    print("Recording...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
    sd.wait()  # Wait until recording is finished
    print("Finished recording")
    return recording, fs

# Function to transcribe audio using OpenAI API
def transcribe_audio(api_key, recording, fs):
    with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
        write(temp_file.name, fs, recording)
        temp_file.seek(0)
        
        with open(temp_file.name, "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file, api_key=api_key)
            return transcript['text'].lower()

# Function to generate speech using OpenAI's text-to-speech API
def text_to_speech(api_key, text):
    response = openai.Audio.create(
        engine="text-davinci-002",
        text=text,
        api_key=api_key
    )
    
    with open("response.mp3", "wb") as audio_file:
        audio_file.write(response['data'])

    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

# Function to get response from ChatGPT
def get_chatgpt_response(api_key, input_text):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": "'you are working inside a wall-e robot. you can only reply with a maximum of 20 words per response, you are humorous and would prefer to reply with simple words instead of complex sentences. also you may be prompted in turkish  if you receive a turkish message respond with turkish only. ignore the hello and merhaba words in every text you are given as these are the voice activation keywords'"
            },
            {
                "role": "user",
                "content": input_text,
            }
        ]
    )
    
    if response and response.choices:
        return response.choices[0].message["content"]
    else:
        print("Error while getting a response from ChatGPT API:", response)
        return "Sorry, I couldn't generate a response at the moment."

def main():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("API key not found. Please set the OPENAI_API_KEY environment variable.")
        return

    keyword_en = "walle"
    keyword_tr = "merhaba"
    stop_keyword = "bye walle"
    
    while True:
        input_text = ""
        
        # Listening for activation keyword
        while not (keyword_en in input_text or keyword_tr in input_text):
            recording, fs = record_audio()
            input_text = transcribe_audio(api_key, recording, fs)
            print("You said:", input_text)

        print("Activated. Listening for commands...")

        # Activated, listen and respond until stop keyword is heard
        while True:
            recording, fs = record_audio()
            input_text = transcribe_audio(api_key, recording, fs)
            print("You said:", input_text)
            
            if stop_keyword in input_text:
                print("Deactivated.")
                break

            response = get_chatgpt_response(api_key, input_text)
            
            # Determine the language of the response (Turkish or English)
            lang = 'tr' if keyword_tr in input_text else 'en'
            text_to_speech(api_key, response)

if __name__ == "__main__":
    main()
