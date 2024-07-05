import os
import openai
import pygame
import time

def listen_microphone(api_key, keyword_en, keyword_tr):
    import sounddevice as sd
    from scipy.io.wavfile import write
    import tempfile

    # Record audio
    fs = 44100  # Sample rate
    seconds = 5  # Duration of recording
    print("Listening for keyword...")
    
    while True:
        print("Recording...")
        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        print("Finished recording")
        
        # Save the recording to a temporary file
        with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
            write(temp_file.name, fs, recording)
            temp_file.seek(0)
            
            # Transcribe audio using OpenAI API
            with open(temp_file.name, "rb") as audio_file:
                transcript = openai.Audio.transcribe("whisper-1", audio_file, api_key=api_key)
                
                text = transcript['text'].lower()
                print("You said:", text)
                if keyword_en in text:
                    return text
                if keyword_tr in text:
                    return text

def text_to_speech(api_key, text):
    # Generate speech using OpenAI's text-to-speech API
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

    keyword_en = "hello"
    keyword_tr = "merhaba"
    
    while True:
        input_text = listen_microphone(api_key, keyword_en, keyword_tr)
        if input_text:
            response = get_chatgpt_response(api_key, input_text)
            
            # Determine the language of the response (Turkish or English)
            lang = 'tr' if keyword_tr in input_text else 'en'
            text_to_speech(api_key, response)

if __name__ == "__main__":
    main()
