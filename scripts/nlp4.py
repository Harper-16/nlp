import time
import requests
from PIL import Image, ImageEnhance, ImageFilter
from io import BytesIO
try:
    from scripts.config import HF_API_KEY
except ImportError:
    from config import HF_API_KEY

MODELS = [
    "black-forest-labs/FLUX.1-schnell",
    "stabilityai/stable-diffusion-xl-base-1.0",
    "runwayml/stable-diffusion-v1-5",
    "CompVis/stable-diffusion-v1-4",
]

API_URL = "https://router.huggingface.co/hf-inference/models/{}"
HEADERS = {"Authorization": f"Bearer {HF_API_KEY}", "Accept": "image/png"}

def generate_image_from_text(prompt):
    """prompt -> PIL.Image (or raises Exception)."""
    payload, last_err = {"inputs": prompt}, None

    for model in MODELS:
        url = API_URL.format(model)

        for _ in range(3):
            try:
                r = requests.post(url, headers=HEADERS, json=payload, timeout=120)
            except Exception as e:
                last_err = f"Connection failed for {model}: {e}"
                break
                
            ct = (r.headers.get("content-type") or "").lower()

            if r.status_code == 503 and "application/json" in ct:
                try:
                    wait_s = float(r.json().get("estimated_time", 5))
                except Exception:
                    wait_s = 5
                time.sleep(wait_s + 1)
                continue

            if r.status_code == 200 and "application/json" not in ct:
                try:
                    return Image.open(BytesIO(r.content)).convert("RGB")
                except Exception as e:
                    last_err = f"Request failed with status code 200: Could not decode image bytes: {e}"
                    break

            try:
                body = r.json() if "application/json" in ct else r.text
            except Exception:
                body = r.text
            last_err = f"Request failed with status code {r.status_code}: {body}"
            break

    raise Exception(last_err or "Request failed with status code 500: Unknown error")

def post_process_image(image):
    """Returns the processed PIL.Image (same I/O as your code)."""
    image = ImageEnhance.Brightness(image).enhance(1.2)
    image = ImageEnhance.Contrast(image).enhance(1.3)
    return image.filter(ImageFilter.GaussianBlur(radius=2))

def main():
    print("Welcome to the Post-Processing Magic Workshop!")
    print("This program generates an image from text and applies post-processing effects.")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("Enter a description for the image (or 'exit' to quit):\n")
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break

        try:
            print("\nGenerating image...")
            image = generate_image_from_text(user_input)
            print("Applying post-processing effects...\n")
            processed_image = post_process_image(image)
            processed_image.show()

            save_option = input("Do you want to save the processed image? (yes/no):\n").strip().lower()
            if save_option == 'yes':
                file_name = input("Enter a name for the image file (without extension):\n").strip()
                processed_image.save(f"{file_name}.png")
                print(f"Image saved as {file_name}.png\n")

            print("-" * 80 + "\n")
        except Exception as e:
            print(f"An error occurred: {e}\n")

if __name__ == "__main__":
    main()
