import threading
import sys
import time
import wave

import matplotlib.pyplot as plt
import numpy as np
import pyaudio
from faster_whisper import WhisperModel


SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
MODEL_SIZE = "base"

stop_event = threading.Event()


def wait_for_enter():
    input("\n🎤 Press Enter to stop recording...\n")
    stop_event.set()


def spinner():
    chars = "|/-\\"
    index = 0
    while not stop_event.is_set():
        sys.stdout.write(f"\r🔴 Recording... {chars[index % len(chars)]}")
        sys.stdout.flush()
        index += 1
        time.sleep(0.1)
    print("\r✅ Recording complete!          ")


def record_audio():
    stop_event.clear()
    audio = pyaudio.PyAudio()
    stream = audio.open(
        format=pyaudio.paInt16,
        channels=1,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE,
    )
    frames = []

    threading.Thread(target=wait_for_enter, daemon=True).start()
    threading.Thread(target=spinner, daemon=True).start()

    try:
        while not stop_event.is_set():
            frames.append(stream.read(CHUNK_SIZE, exception_on_overflow=False))
    finally:
        stream.stop_stream()
        stream.close()
        sample_width = audio.get_sample_size(pyaudio.paInt16)
        audio.terminate()

    return b"".join(frames), SAMPLE_RATE, sample_width


def save_audio(data, rate, width, filename="recording.wav"):
    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(width)
        wav_file.setframerate(rate)
        wav_file.writeframes(data)
    print(f"💾 Saved: {filename}")


def transcribe_local(data, rate, width, model):
    with wave.open("_stt_input.wav", "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(width)
        wav_file.setframerate(rate)
        wav_file.writeframes(data)

    segments, _ = model.transcribe("_stt_input.wav", vad_filter=True)
    text = " ".join(segment.text.strip() for segment in segments).strip()
    if text:
        print(f"📝 Transcription: {text}")
    else:
        print("❌ Could not understand audio")


def plot_waveform(data, rate):
    samples = np.frombuffer(data, dtype=np.int16)
    time_axis = np.linspace(0, len(samples) / rate, len(samples))
    plt.figure(figsize=(10, 4))
    plt.plot(time_axis, samples, color="blue")
    plt.title("Your Voice Waveform")
    plt.xlabel("Time (seconds)")
    plt.ylabel("Amplitude")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def main():
    print("=" * 40)
    print("🎙️  LOCAL SPEECH TO TEXT")
    print("=" * 40)
    print(f"Loading local Whisper model: {MODEL_SIZE}")
    print("The first run downloads the model; transcription then runs locally.\n")

    model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")
    print("Speak into your microphone...")

    audio_data, rate, width = record_audio()
    save_audio(audio_data, rate, width)
    transcribe_local(audio_data, rate, width, model)
    plot_waveform(audio_data, rate)


if __name__ == "__main__":
    main()
