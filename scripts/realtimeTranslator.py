import speech_recognition as sr
import colorama
import pyttsx3

colorama.init(autoreset=True)

try:
    from googletrans import Translator
except Exception as _import_err:  # e.g. googletrans 4.0.0rc1 vs httpcore/httpx mismatch
    Translator = None
    _IMPORT_ERROR = _import_err
else:
    _IMPORT_ERROR = None

def speak(text, language='en'):
    engine = pyttsx3.init()
    engine.setProperty('rate', 150)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)

    voices = engine.getProperty('voices') or []
    lang_index = {'en': 0, 'es': 1, 'hi': 2, 'ml': 3, 'ta': 4, 'te': 5, 'kn': 6, 'bn': 7}.get(language, 0)
    if voices:
        engine.setProperty('voice', voices[lang_index].id if lang_index < len(voices) else voices[0].id)

    engine.say(text)
    engine.runAndWait()


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

def translate_text(text, target_language='es'):
    if Translator is None:
        print(colorama.Fore.RED + f"Translator unavailable (googletrans import failed: {_IMPORT_ERROR}).")
        print(colorama.Fore.YELLOW + "Fix: pip install \"httpx==0.13.3\" \"httpcore==0.9.*\" --force-reinstall  OR  pip install deep-translator")
        return text
    try:
        translator_instance = Translator()
        translation = translator_instance.translate(text, dest=target_language)
        print(translation.text)
        return translation.text
    except Exception as e:
        print(colorama.Fore.RED + f"Translation failed: {e}")
        return text

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

    choice = input(colorama.Fore.CYAN + "Enter the number corresponding to your choice: ").strip()
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