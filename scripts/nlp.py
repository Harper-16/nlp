import requests
try:
    from scripts.config import HF_API_KEY
except ImportError:
    from config import HF_API_KEY
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

# Default model name that can be easily changed
DEFAULT_MODEL = "google/pegasus-xsum"


def build_api_url(model_name):
    return f"https://api-inference.huggingface.co/models/{model_name}"


def query(payload, model_name=DEFAULT_MODEL):
    """
    Sends a POST request to the Hugging Face API with robust
    error handling for offline states.
    """
    api_url = build_api_url(model_name)
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=10)
        return response.json()
    except requests.exceptions.ConnectionError:
        print(Fore.RED + "\n❌ Connection Error: Unable to reach Hugging Face. Check your internet connection or DNS.")
        return {"error": "Network unreachable"}
    except requests.exceptions.Timeout:
        print(Fore.RED + "\n❌ Timeout Error: The request took too long to respond.")
        return {"error": "Request timed out"}
    except requests.exceptions.RequestException as e:
        print(Fore.RED + f"\n❌ Request Error: {e}")
        return {"error": str(e)}



def summarize_text(text, min_length, max_length, model_name=DEFAULT_MODEL):
    payload = {
        "inputs": text,
        "parameters": {"min_length": min_length, "max_length": max_length}
    }
    
    print(Fore.BLUE + Style.BRIGHT + f"\n???? Performing AI summarization using model: {model_name}")
    
    result = query(payload, model_name=model_name)
    
    # Check if the response has the expected format
    if isinstance(result, list) and result and "summary_text" in result[0]:
        return result[0]["summary_text"]
    else:
        print(Fore.RED + "❌ Error in summarization response:", result)
        return None


if __name__ == "__main__":
    # Ask for the user's name
    print(Fore.YELLOW + Style.BRIGHT + "???? Hi there! What's your name?")
    user_name = input("Your name: ").strip()

    if not user_name:
        user_name = "User"

    print(Fore.GREEN + f"Welcome, {user_name}! Let's give your text some AI magic ✨.")

    # Prompt the user for text input
    print(Fore.YELLOW + Style.BRIGHT + "\nPlease enter the text you want to summarize:")
    user_text = input("> ").strip()

    if not user_text:
        print(Fore.RED + "❌ No text provided. Exiting.")
    else:
        # Ask the user for the model they want to use
        print(Fore.YELLOW + "\nEnter the model name you want to use (e.g., facebook/bart-large-cnn):")
        model_choice = input("Model name (leave blank for default): ").strip()

        if not model_choice:
            model_choice = DEFAULT_MODEL

        # Ask for the summarization style
        print(Fore.YELLOW + "\nChoose your summarization style:")
        print("1. Standard Summary (Quick & concise)")
        print("2. Enhanced Summary (More detailed and refined)")
        
        style_choice = input("Enter 1 or 2: ").strip()

        if style_choice == "2":
            min_length = 80
            max_length = 200
            print(Fore.BLUE + "Enhancing summarization process... ????")
        else:
            min_length = 50
            max_length = 150
            print(Fore.BLUE + "Using standard summarization settings... ????")
        summary = summarize_text(user_text, min_length, max_length, model_name=model_choice)
        if summary:
            print(Fore.GREEN + Style.BRIGHT + f"\n???? AI Summarizer Output for {user_name}:")
            print(Fore.GREEN + summary)

