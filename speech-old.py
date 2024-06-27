import speech_recognition as sr
import requests
import pygame
import time
from gtts import gTTS

def listen_microphone(keyword_en, keyword_tr):
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening for keyword...")
        while True:
            audio = r.listen(source)
            try:
                print("Recognizing...")
                text = r.recognize_google(audio, language='en-US').lower()
                print("You said:", text)
                if keyword_en in text:
                    return text
                text_tr = r.recognize_google(audio, language='tr-TR').lower()
                print("Söylediniz:", text_tr)
                if keyword_tr in text_tr:
                    return text_tr
            except sr.UnknownValueError:
                print("Sorry, I could not understand audio.")
            except sr.RequestError as e:
                print("Error connecting to Google Speech Recognition service:", str(e))


def text_to_speech(text, voice='male', lang='en'):
    tts = gTTS(text=text, lang=lang)
    tts.save("response.mp3")
    pygame.mixer.init()
    pygame.mixer.music.load("response.mp3")
    pygame.mixer.music.set_volume(1.0)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(1)

def get_chatgpt_response(input_text, api_key):
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}',
    }
    
    data = {
        'messages': [
            {
        "role": "system",
        "content": "'you are working inside a wall-e robot. you can oly reply with a maxiumum of 20 words per response, you are humorous and would prefer to reply with simple words instead of complex sentences. also you may be prompted in turkish  if you recieve a turkish messeage respond with turkish only. ignore the hello and merhaba words in every text you are given as these are the voice activation keywords'"
      },
            {
                'role': 'user',
                'content': input_text,
            }
        ],
        'model': 'gpt-3.5-turbo',  # Specify the model to use
    }
    response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
    if response.status_code == 200:
		
        return response.json()['choices'][0]['message']['content']
    else:
        print("Error while getting a response from ChatGPT API:", response.text)
        return "Sorry, I couldn't generate a response at the moment."

def main():
    # Your ChatGPT API key
    api_key = os.getenv("CHATGPT_API_KEY")
    if not api_key:
        print("API key not found. Please set the CHATGPT_API_KEY environment variable.")
        return "Sorry, I couldn't generate a response at the moment."

    keyword_en = "hello"
    keyword_tr = "merhaba"
    
    while True:
        input_text = listen_microphone(keyword_en, keyword_tr)
        if input_text:
            response = get_chatgpt_response(input_text, api_key)
            
            # Determine the language of the response (Turkish or English)
            lang = 'tr' if keyword_tr in input_text else 'en'
            text_to_speech(response, lang=lang)

                
if __name__ == "__main__":
    main()
