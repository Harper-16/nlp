import speech_recognition as sr
from googletrans import Translator
import os
import shlex
import colorama

colorama.init(autoreset=True)

def speak(text,language='en'):
    # use espeak instead
    os.system(f"espeak {shlex.quote(text)}") 
    

def stt():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            print(colorama.Fore.GREEN + f"You said: {text}")
            return text
        except sr.UnknownValueError:
            print(colorama.Fore.RED + "Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            print(colorama.Fore.RED + "Could not request results; check your network connection.")
            return None


def translate_text(text,target_language='es'):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    print(translation.text)
    return translation.text

def display_language_options():
    print(colorama.Fore.YELLOW + "Available languages:")
    print("1. English (en)")
    print("2. Spanish (es)")
    print("3. Hindi (hi)")
    print("4. Malayalam (ml)")
    print("5. Tamil (ta)")
    print("6. Telugu (te)")
    print("7. Kannada (kn)")
    print("8. Bengali (bn)")

    choice = input(colorama.Fore.CYAN + "Enter the number corresponding to your choice: ")
    language_dict = {
        '1': 'en',
        '2': 'es', 
        '3': 'hi',
        '4': 'ml',
        '5': 'ta',
        '6': 'te',
        '7': 'kn',
        '8': 'bn'
    }
    return language_dict.get(choice, 'en')  # Default to English if invalid choice

def main():
    target_language = display_language_options()
    original_text = stt()
    if original_text:
        translated_text = translate_text(original_text, target_language)
        speak(translated_text, target_language)

if __name__ == "__main__":
    main()