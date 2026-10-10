from datetime import datetime
import speech_recognition as sr
import pyttsx3
import wikipedia

# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty("rate", 160)


def speak(text: str) -> None:
    """Converts text to speech and prints the spoken response."""
    print(f"🤖 Assistant: {text}")
    engine.say(text)
    engine.runAndWait()


def search_wikipedia(query: str) -> str:
    """Fetches a short summary from Wikipedia for simple questions."""
    try:
        # Get a 1-sentence summary
        summary = wikipedia.summary(query, sentences=1)
        return summary
    except wikipedia.DisambiguationError:
        return "There are too many results for that topic. Please be more specific."
    except wikipedia.PageError:
        return "I couldn't find any information on that."
    except Exception:
        return "I had trouble searching for that."


def get_audio() -> str:
    """Captures audio input from the microphone and returns speech as text."""
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:
        print("\n🎙️  Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.8)

        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            print("⏳ Processing speech...")

            command = recognizer.recognize_google(audio)
            print(f"🗣️  You said: '{command}'")
            return command.lower()

        except sr.WaitTimeoutError:
            print("⚠️  No speech detected within time limit.")
        except sr.UnknownValueError:
            print("❌ Could not understand audio.")
        except sr.RequestError as e:
            print(f"❌ Speech service error: {e}")

    return ""


def respond_to_command(command: str) -> bool:
    """Handles commands locally or searches Wikipedia."""
    if not command:
        return True

    # Greetings
    if any(word in command for word in ["hello", "hi", "hey"]):
        speak("Hi there! How can I help you today?")

    # Name check
    elif "your name" in command:
        speak("I am your simple Python voice assistant.")

    # Time check
    elif "time" in command:
        current_time = datetime.now().strftime("%I:%M %p")
        speak(f"The current time is {current_time}.")

    # Exit
    elif any(word in command for word in ["exit", "stop", "quit", "bye"]):
        speak("Goodbye!")
        return False

    # Wikipedia fallback for simple searches (e.g. "who is Albert Einstein")
    else:
        print("🔍 Searching Wikipedia...")
        answer = search_wikipedia(command)
        speak(answer)

    return True


def main():
    speak("Voice assistant activated. Ask me anything!")

    running = True
    while running:
        command = get_audio()
        running = respond_to_command(command)


if __name__ == "__main__":
    main()
